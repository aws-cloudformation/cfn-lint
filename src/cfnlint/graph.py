import re
import six
from networkx import networkx

class Graph(object):
    """Models a template as a directed graph of resources"""

    def __init__(self, cfn):
        """Builds a graph where resources are nodes and edges are explicit (DependsOn) or implicit (Fn::GetAtt, Fn::Sub, Ref)
        relationships between resources"""

        # Directed graph that allows self loops and parallel edges
        self.graph = networkx.MultiDiGraph()

        # add all resources in the template as nodes
        for resourceId in cfn.template['Resources'].keys():
            self.graph.add_node(resourceId)

        # add edges for "Ref" tags. { "Ref" : "logicalNameOfResource" }
        refs_paths = cfn.search_deep_keys('Ref')
        for ref_path in refs_paths:
            ref_type, source_id = ref_path[:2]
            target_id = ref_path[-1]
            if not ref_type == 'Resources':
                continue

            if isinstance(target_id, (six.text_type, six.string_types, int)) and (self._is_resource(cfn, target_id)):
                target_resource_id = target_id
                self.graph.add_edge(source_id, target_resource_id, label='Ref')

        # add edges for "Fn::GetAtt" tags. { "Fn::GetAtt" : [ "logicalNameOfResource", "attributeName" ] }
        getatt_paths = cfn.search_deep_keys('Fn::GetAtt')
        for getatt_path in getatt_paths:
            ref_type, source_id = getatt_path[:2]
            value = getatt_path[-1]
            if not ref_type == 'Resources':
                continue

            if isinstance(value, list) and len(value) == 2 and (self._is_resource(cfn, value[0])):
                target_resource_id = value[0]
                self.graph.add_edge(source_id, target_resource_id, label='Fn::GetAtt')

        # add edges for "DependsOn" tags. { "DependsOn" : [ String, ... ] }
        depends_on_paths = cfn.search_deep_keys('DependsOn')
        for depend_on_path in depends_on_paths:
            ref_type, source_id = depend_on_path[:2]
            target_ids = depend_on_path[-1]
            if not ref_type == 'Resources':
                continue

            if isinstance(target_ids, (six.text_type, six.string_types)):
                target_ids = [target_ids]
            for target_id in target_ids:
                if self._is_resource(cfn, target_id):
                    target_resource_id = target_id
                    self.graph.add_edge(source_id, target_resource_id, label='DependsOn')

        # add edges for "Fn::Sub" tags. E.g. { "Fn::Sub": "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:vpc/${vpc}" }
        sub_objs = cfn.search_deep_keys('Fn::Sub')
        for sub_obj in sub_objs:
            sub_parameters = []
            sub_parameter_values = {}
            value = sub_obj[-1]
            ref_type, source_id = sub_obj[:2]

            if not ref_type == 'Resources':
                continue

            if isinstance(value, list):
                if not value:
                    continue
                if len(value) == 2:
                    sub_parameter_values = value[1]
                sub_parameters = self._find_parameter(value[0])
            elif isinstance(value, (six.text_type, six.string_types)):
                sub_parameters = self._find_parameter(value)

            for sub_parameter in sub_parameters:
                if sub_parameter not in sub_parameter_values:
                    if '.' in sub_parameter:
                        sub_parameter = sub_parameter.split('.')[0]
                    if self._is_resource(cfn, sub_parameter):
                        self.graph.add_edge(source_id, sub_parameter, label='Fn::Sub')

    def get_cycles(self, cfn):
        """Return all resource pairs that have a cycle in them"""
        result = []
        for starting_resource in cfn.template.get('Resources', {}):
            try:
                for edge in list(networkx.find_cycle(self.graph, starting_resource)):
                    if edge not in result:
                        result.append(edge)
            except networkx.NetworkXNoCycle:
                continue
        return result

    def _is_resource(self, cfn, identifier):
        """Check if the identifier is that of a Resource"""
        return cfn.template.get('Resources', {}).get(identifier, {})

    def _find_parameter(self, string):
        """Search string for tokenized fields"""
        regex = re.compile(r'\${([a-zA-Z0-9.]*)}')
        return regex.findall(string)
