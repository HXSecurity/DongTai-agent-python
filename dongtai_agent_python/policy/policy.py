from dongtai_agent_python.setting import const


def new_policy_rule(rule_type, detail):
    signature = detail.get('value', '')
    if signature == '':
        return None
    if rule_type not in const.NODE_TYPES:
        return None
    return PolicyRule(rule_type, signature, detail.get('source', None), detail.get('target', None))


class PolicyRule(object):
    def __init__(self, node_type, signature, source=None, target=None):
        self.node_type = node_type
        self.signature = signature

        splits = signature.split(".")
        self.class_name = splits[-2]
        self.method_name = splits[-1]
        self.fully_class_name = signature[:-len(self.method_name) - 1]

        self.origin_method = None
        self.patched_method = None

        self.source_from = TaintFrom(const.TAINT_SOURCE, source)
        self.target_from = TaintFrom(const.TAINT_TARGET, target)

    def set_origin_method(self, origin_method):
        self.origin_method = origin_method

    def set_patched_method(self, patched_method):
        self.patched_method = patched_method

    def get_source_taints(self, self_obj, result, args, kwargs):
        return self.source_from.get_taints(self_obj, result, args, kwargs)

    def get_target_taints(self, self_obj, result, args, kwargs):
        return self.target_from.get_taints(self_obj, result, args, kwargs)


class TaintFrom(object):
    def __init__(self, taint_type, source_or_target):
        self.taint_type = taint_type
        self.source_or_target = source_or_target

        self.from_object = False
        self.from_return = False
        self.from_all_parameters = False
        self.from_args = []
        self.from_kwargs = []

        self.parse_from()

    def parse_from(self):
        if not self.source_or_target:
            if self.taint_type == const.TAINT_SOURCE:
                self.from_all_parameters = True
            else:
                self.from_return = True
            return

        if self.source_or_target == 'P':
            self.from_all_parameters = True
            return

        splits = self.source_or_target.split('|')
        for sp in splits:
            if sp == 'O':
                self.from_object = True
            elif sp == 'R':
                self.from_return = True
            elif sp.startswith('P'):
                if sp == 'P':
                    self.from_all_parameters = True
                if self.from_all_parameters:
                    continue

                sp = sp[1:]
                args = sp.split(',')
                for arg in args:
                    if arg.isdigit():
                        idx = int(arg) - 1
                        if idx < 0:
                            continue
                        self.from_args.append(idx)
                    else:
                        self.from_kwargs.append(arg)

    def get_taints(self, self_obj, result, args, kwargs):
        taints = []
        if self.from_object:
            taints.append(self_obj)

        if self.from_return:
            taints.append(result)

        if self.from_all_parameters:
            if args:
                for v in args:
                    taints.append(v)
            if kwargs:
                for k in kwargs:
                    taints.append(kwargs[k])
        else:
            if args and self.from_args:
                for idx in self.from_args:
                    if idx < len(args):
                        taints.append(args[idx])
            if kwargs and self.from_kwargs:
                for k in self.from_kwargs:
                    if k in kwargs:
                        taints.append(kwargs[k])

        return taints
