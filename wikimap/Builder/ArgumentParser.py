class BuildArgumentParser(object):
    def __init__(self, build):
        self._build = build

    def parse_job_ranges(self, multi_range_string):
        max_job_number = len(self._build) - 1
        num_only_ranges = self._replace_aliases_with_nums(multi_range_string)
        range_strings = num_only_ranges.split(',')
        jobs_in_ranges = []
        for rs in range_strings:
            rs = rs.strip()
            sep_pos = rs.find('-')
            if sep_pos == -1:
                if rs == '*':
                    jobs_in_ranges.extend(range(0, max_job_number+1))
                elif rs == '':
                    pass
                else:
                    jobs_in_ranges.append(int(rs))
            elif sep_pos == 0:
                jobs_in_ranges.extend(range(0, int(rs[1:]) + 1))
            elif sep_pos == len(rs) - 1:
                jobs_in_ranges.extend(range(int(rs[:-1]), max_job_number + 1))
            else:
                jobs_in_ranges.extend(range(int(rs[:sep_pos]), int(rs[sep_pos+1:]) + 1))
        return set(jobs_in_ranges)

    def _replace_aliases_with_nums(self, string):
        alias_2_num = self._get_alias_2_num()
        aliases = alias_2_num.keys()
        aliases.sort(key=len, reverse=True)
        for alias in aliases:
            string = string.replace(alias, str(alias_2_num[alias]))
        return string

    def _get_alias_2_num(self):
        alias_2_num = {}
        for job in self._build:
            if len(job.alias) > 0:
                alias_2_num[job.alias] = job.number
        return alias_2_num
