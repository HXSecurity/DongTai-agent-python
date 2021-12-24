from dongtai_agent_python.setting import const


def new_policy_rule(rule_type, detail):
    signature = detail.get('value', '')
    if signature == '':
        return None
    if rule_type not in const.NODE_TYPES:
        return None
    return PolicyRule(rule_type, signature, detail.get('source', None), detail.get('target', None))


class PolicyRule(object):
    def __init__(self, rule_type, signature, source=None, target=None):
        self.rule_type = rule_type
        self.signature = signature

        # @TODO: build patch for signature

        self.source_from = TaintFrom(const.TAINT_SOURCE, source)
        self.target_from = TaintFrom(const.TAINT_TARGET, target)


class TaintFrom(object):
    def __init__(self, taint_type, source_or_target):
        self.taint_type = taint_type
        self.source_or_target = source_or_target

        self.from_object = False
        self.from_return = False
        self.from_all_parameters = False
        self.from_args = set()
        self.from_kwargs = set()

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
                        self.from_args.add(idx)
                    else:
                        self.from_kwargs.add(arg)
