import ast

class BuildArgumentParser(object):
    def __init__(self, build):
        self._build = build

    def parse_job_ranges(self, multi_range_string):
        max_job_number = len(self._build) - 1
        num_only_ranges = self._replace_tags_with_nums(multi_range_string)
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

    def parse_config(self, config_string):
        config = ast.literal_eval(config_string) # literal_eval only evaluates basic types instead of arbitrary code
        for job_name_or_tag, job_config in config.iteritems():
            del config[job_name_or_tag]
            config[self._replace_tag_with_name(job_name_or_tag)] = job_config
        return config

    def _replace_tags_with_nums(self, string):
        tag_2_num = self._get_tag_2_num()
        tags = tag_2_num.keys()
        tags.sort(key=len, reverse=True)
        for tag in tags:
            string = string.replace(tag, str(tag_2_num[tag]))
        return string

    def _replace_tag_with_name(self, string):
        tag_2_name = self._get_tag_2_name()
        return tag_2_name[string] if string in tag_2_name else string

    def _get_tag_2_num(self):
        tag_2_num = {}
        for job in self._build:
            if len(job.tag) > 0:
                tag_2_num[job.tag] = job.number
        return tag_2_num

    def _get_tag_2_name(self):
        tag_2_name = {}
        for job in self._build:
            if len(job.tag) > 0:
                tag_2_name[job.tag] = job.name
        return tag_2_name
