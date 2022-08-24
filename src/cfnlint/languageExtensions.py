from cfnlint.rules import RuleMatch

class LanguageExtensions(object):
    """Class for a CloudFormation languageExtensions"""

    def validate_transform_is_declared(self, has_language_extensions_transform, matches, tree, intrinsic_function):
        if not has_language_extensions_transform:
            message = 'Missing Transform: Declare the AWS::LanguageExtensions Transform globally to enable use' \
                      ' of the intrinsic function ' + intrinsic_function + ' at {0}'
            matches.append(RuleMatch(tree[:], message.format('/'.join(map(str, tree)))))
        return matches

    def validate_type(self, fn_object_val, matches, tree, intrinsic_function):
        if not isinstance(fn_object_val, dict) and not isinstance(fn_object_val, list):
            message = intrinsic_function + ' needs a map at {0}'
            matches.append(RuleMatch(tree[:], message.format('/'.join(map(str, tree)))))
        elif len(fn_object_val) == 0:
            message = 'Invalid value for '+intrinsic_function+' for {0}'
            matches.append(RuleMatch(tree[:], message.format('/'.join(map(str, tree)))))
        return matches

    def validate_pseudo_parameters(self, fn_object_val, matches, tree, pseudo_params, intrinsic_function):
        if isinstance(fn_object_val, dict):
            ref = 'Ref'
            ref_list = [val[ref] for key, val in fn_object_val.items() if ref in val]
            for ref in ref_list:
                if ref in pseudo_params:
                    message = intrinsic_function + ' does not support the pseudo parameter ' + ref + ' for {0}'
                    matches.append(RuleMatch(tree[:], message.format('/'.join(map(str, tree)))))
        return matches
