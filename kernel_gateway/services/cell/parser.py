import re
import sys

class EndpointSortStrategies(object):

    @staticmethod
    def first_path_param_index(endpoint):
        '''Returns the index to the first path parameter for the endpoint. The
        index is not the string index, but rather where it is within the path.
        For example:
            first_path_param_index('/foo/:bar') # returns 1
            first_path_param_index('/foo/quo/:bar') # return 2
            first_path_param_index('/foo/quo/bar') # return sys.maxsize
        '''
        index = sys.maxsize
        if endpoint.find(':') >= 0:
            index = endpoint.count('/', 0, endpoint.find(':')) - 1
        return index

class APICellParser(object):
    kernelspec_comment_mapping = {
        None:'#',
        'scala':'//'
    }
    api_indicator = '{}\s+(GET|PUT|POST|DELETE)\s+(\/.*)+'

    def __init__(self, kernelspec):
        try:
            prefix = self.kernelspec_comment_mapping[kernelspec]
        except KeyError:
            prefix = self.kernelspec_comment_mapping[None]
        self.kernelspec_api_indicator = re.compile(self.api_indicator.format(prefix))

    def is_api_cell(self, cell_source):
        '''Determines if the cell source is decroated to indicate an api cell'''
        match = self.kernelspec_api_indicator.match(cell_source)
        return match is not None

    def endpoints(self, source_cells, sort_func=EndpointSortStrategies.first_path_param_index):
        '''Return a list of tuples containing the method+URI and the cell source'''
        endpoints = {}
        for cell_source in source_cells:
            if self.is_api_cell(cell_source):
                matched = self.kernelspec_api_indicator.match(cell_source)
                uri = matched.group(2).strip()
                verb = matched.group(1)
                if uri not in endpoints:
                    endpoints[uri] = {}
                if verb not in endpoints[uri]:
                    endpoints[uri][verb] = cell_source
        sorted_keys = sorted(endpoints, key=sort_func, reverse=True)
        ret_val = []
        for key in sorted_keys:
            ret_val.append((key,endpoints[key]))
        return ret_val
