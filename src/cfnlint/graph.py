"""
Helpers for loading resources, managing specs, constants, etc.

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
import re
import warnings
from typing import Any, List
import networkx


LOGGER = logging.getLogger('cfnlint.graph')


class EdgeSetting:
    color: str = 'black'
    labal: str = ''

    def __init__(self, color: str, label: str) -> None:
        self.color = color
        self.label = label


class NodeSetting:
    color: str = 'black'
    shape: str
    node_type: str

    def __init__(self, color: str, node_type: str, shape: str = 'ellipse') -> None:
        self.color = color
        self.shape = shape
        self.node_type = node_type


class GraphSettings:
    ref: EdgeSetting
    getatt: EdgeSetting
    depends_on: EdgeSetting
    resource: NodeSetting
    parameter: NodeSetting
    output: NodeSetting

    def subgraph_view(self, graph) -> networkx.MultiDiGraph:
        view = networkx.MultiDiGraph(name='template')
        resources: List[str] = [
            n for n, v in graph.nodes.items() if v['type'] in ['Resource']
        ]
        view.add_nodes_from((n, graph.nodes[n]) for n in resources)
        view.add_edges_from(
            (n, nbr, key, d)
            for n, nbrs in graph.adj.items()
            if n in resources
            for nbr, keydict in nbrs.items()
            if nbr in resources
            for key, d in keydict.items()
        )
        view.graph.update(graph.graph)
        return view


class DefaultGraphSettings(GraphSettings):
    ref = EdgeSetting(color='black', label='Ref')
    getatt = EdgeSetting(color='black', label='GetAtt')
    depends_on = EdgeSetting(color='black', label='DependsOn')
    resource = NodeSetting(color='black', node_type='Resource')
    parameter = NodeSetting(color='black', node_type='Parameter', shape='box')
    output = NodeSetting(color='black', node_type='Output', shape='box')


class Graph:
    """Models a template as a directed graph of resources"""

    settings: GraphSettings
    __supported_types: List[str] = ['Resources', 'Parameters', 'Outputs']

    def __init__(self, cfn):
        """Builds a graph where resources are nodes and edges are explicit (DependsOn) or implicit (Fn::GetAtt, Fn::Sub, Ref)
        relationships between resources"""

        self.settings = DefaultGraphSettings()

        # Directed graph that allows self loops and parallel edges
        self.graph = networkx.MultiDiGraph(name='template')

        self._add_resources(cfn)
        self._add_parameters(cfn)
        self._add_outputs(cfn)
        self._add_refs(cfn)
        self._add_getatts(cfn)
        self._add_subs(cfn)

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

    def _add_parameters(self, cfn: Any) -> None:
        # add all parameters in the template as nodes
        for parameter_id, parameter_values in cfn.template.get(
            'Parameters', {}
        ).items():
            if not isinstance(parameter_values, dict):
                continue
            type_val = parameter_values.get('Type', '')
            if not isinstance(type_val, str):
                continue
            graph_label = str.format(f'"{parameter_id}\\n<{type_val}>"')
            self._add_node(
                parameter_id, label=graph_label, settings=self.settings.parameter
            )

    def _add_outputs(self, cfn: Any) -> None:
        # add all outputs in the template as nodes
        for output_id in cfn.template.get('Outputs', {}).keys():
            graph_label = str.format(f'"{output_id}"')
            self._add_node(output_id, label=graph_label, settings=self.settings.output)

    def _add_resources(self, cfn: Any):
        # add all resources in the template as nodes
        for resourceId, resourceVals in cfn.template.get('Resources', {}).items():
            if not isinstance(resourceVals, dict):
                continue
            type_val = resourceVals.get('Type', '')
            if not isinstance(type_val, str):
                continue
            graph_label = str.format(f'"{resourceId}\\n<{type_val}>"')
            self._add_node(
                resourceId, label=graph_label, settings=self.settings.resource
            )
            target_ids = resourceVals.get('DependsOn', [])
            if isinstance(target_ids, (list, str)):
                if isinstance(target_ids, (str)):
                    target_ids = [target_ids]
                for target_id in target_ids:
                    if isinstance(target_id, str):
                        if self._is_resource(cfn, target_id):
                            self._add_edge(
                                resourceId,
                                target_id,
                                ['DependsOn'],
                                self.settings.depends_on,
                            )

    def _add_refs(self, cfn: Any) -> None:
        # add edges for "Ref" tags. { "Ref" : "logicalNameOfResource" }
        refs_paths = cfn.search_deep_keys('Ref')
        for ref_path in refs_paths:
            ref_type, source_id = ref_path[:2]
            source_path = ref_path[2:-2]
            target_id = ref_path[-1]
            if not ref_type in self.__supported_types:
                continue

            if ref_type in ['Parameters', 'Outputs']:
                source_id = f'{ref_type[:-1]}-{source_id}'

            if isinstance(target_id, (str, int)) and (
                self._is_resource(cfn, target_id)
            ):
                self._add_edge(source_id, target_id, source_path, self.settings.ref)

    def _add_getatts(self, cfn: Any) -> None:
        # add edges for "Fn::GetAtt" tags.
        # { "Fn::GetAtt" : [ "logicalNameOfResource", "attributeName" ] } or { "!GetAtt" : "logicalNameOfResource.attributeName" }
        getatt_paths = cfn.search_deep_keys('Fn::GetAtt')
        for getatt_path in getatt_paths:
            ref_type, source_id = getatt_path[:2]
            source_path = getatt_path[2:-2]
            value = getatt_path[-1]
            if not ref_type in self.__supported_types:
                continue

            if ref_type in ['Parameters', 'Outputs']:
                source_id = f'{ref_type[:-1]}-{source_id}'

            if (
                isinstance(value, list)
                and len(value) == 2
                and (self._is_resource(cfn, value[0]))
            ):
                target_resource_id = value[0]
                self._add_edge(
                    source_id, target_resource_id, source_path, self.settings.getatt
                )

            if isinstance(value, (str, str)) and '.' in value:
                target_resource_id = value.split('.')[0]
                if self._is_resource(cfn, target_resource_id):
                    self._add_edge(
                        source_id, target_resource_id, source_path, self.settings.getatt
                    )

    def _add_subs(self, cfn: Any) -> None:
        # add edges for "Fn::Sub" tags. E.g. { "Fn::Sub": "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:vpc/${vpc}" }
        sub_objs = cfn.search_deep_keys('Fn::Sub')
        for sub_obj in sub_objs:
            sub_parameters = []
            sub_parameter_values = {}
            value = sub_obj[-1]
            source_path = sub_obj[2:-2]
            ref_type, source_id = sub_obj[:2]

            if not ref_type in self.__supported_types:
                continue

            if ref_type in ['Parameters', 'Outputs']:
                source_id = f'{ref_type[:-1]}-{source_id}'

            if isinstance(value, list):
                if not value:
                    continue
                if len(value) == 2:
                    sub_parameter_values = value[1]
                sub_parameters = self._find_parameter(value[0])
            elif isinstance(value, (str)):
                sub_parameters = self._find_parameter(value)

            for sub_parameter in sub_parameters:
                if sub_parameter not in sub_parameter_values:
                    if '.' in sub_parameter:
                        target_id = sub_parameter.split('.')[0]
                        if self._is_resource(cfn, target_id):
                            self._add_edge(
                                source_id, target_id, source_path, self.settings.getatt
                            )
                    elif self._is_resource(cfn, sub_parameter):
                        self._add_edge(
                            source_id, sub_parameter, source_path, self.settings.ref
                        )

    def _add_node(self, node_id, label, settings):
        if settings.node_type in ['Parameter', 'Output']:
            node_id = f'{settings.node_type}-{node_id}'

        self.graph.add_node(
            node_id,
            label=label,
            color=settings.color,
            shape=settings.shape,
            type=settings.node_type,
        )

    def _add_edge(self, source_id, target_id, source_path, settings):
        self.graph.add_edge(
            source_id,
            target_id,
            source_paths=source_path,
            label=settings.label,
            color=settings.color,
        )

    def _is_resource(self, cfn, identifier):
        """Check if the identifier is that of a Resource"""
        return cfn.template.get('Resources', {}).get(identifier, {})

    def _find_parameter(self, string):
        """Search string for tokenized fields"""
        regex = re.compile(r'\${([a-zA-Z0-9.]*)}')
        return regex.findall(string)

    # pylint: disable=import-outside-toplevel,unused-variable
    def to_dot(self, path):
        """Export the graph to a file with DOT format"""
        view = self.settings.subgraph_view(self.graph)
        try:
            import pygraphviz  # pylint: disable=unused-import

            networkx.drawing.nx_agraph.write_dot(view, path)
        except ImportError:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', category=PendingDeprecationWarning)
                    import pydot  # pylint: disable=unused-import

                    networkx.drawing.nx_pydot.write_dot(view, path)
            except ImportError as e:
                raise e
