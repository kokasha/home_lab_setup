from ipaddress import IPv4Network

class FilterModule(object):
    def filters(self):
        return {
            'find_matching_entry': self.find_matching_entry,
            'filter_pyats_ios_pfx_list': self.filter_pyats_ios_pfx_list
        }

    @staticmethod
    def build_input_prefix(prefix, prefixlength_range):
        '''
        :param prefix: IPv4 prefix in this form 10.1.1.0/24
        :param prefixlength_range: prefix_length in this form 24..28
        :return: list of all prefix
        Example:
        ========
        prefix = '10.1.1.0/24'
        prefixlength_range = '25..27'

        return value = ['10.1.1.0/25','10.1.1.0/26','10.1.1.0/27'] 
        '''
        network, netmask = prefix.split('/')
        min_netmask , max_netmask = prefixlength_range.split('..')

        final_prefix_list = list()
        for i in range( int(min_netmask), int(max_netmask)+1 ):
            final_prefix_list.append(network + '/' + str(i))
        
        return final_prefix_list

    @staticmethod
    def is_matching_prefix(prefix_to_test, prefix_list_entry, netmask_range):
        '''
        This Function tests if a given prefix is matched by an Entry in 
        a prefix list

        Example:
        ========
        prefix_to_test = '10.1.1.0/24'
        prefix_list_entry = '10.1.0.0/16
        '''

        min_mask = int(netmask_range.split('..')[0])
        max_mask = int(netmask_range.split('..')[1])

        # Match On 0.0.0.0/0 Prefixes
        if prefix_list_entry == '0.0.0.0/0':

            # Match Default Route ONLY
            if prefix_to_test == '0.0.0.0/0' and netmask_range == '0..0':
                return True

            if min_mask <= IPv4Network(prefix_to_test).prefixlen <= max_mask:
                return True
            else:
                return False
                
        if IPv4Network(prefix_to_test).subnet_of(IPv4Network(prefix_list_entry)) and \
            min_mask <= IPv4Network(prefix_to_test).prefixlen <= max_mask:
            return True
        else:
            return False

        # pfx_entry_list = build_input_prefix(prefix_list_entry,netmask_range)

        # for i in pfx_entry_list:
        #     if IPv4Network(prefix_to_test).subnet_of(IPv4Network(i)) and \
        #         min_mask <= IPv4Network(prefix_to_test).prefixlen <= max_mask:
        #         return True
        # else:
        #     return False

    def find_matching_entry(self,prefix_list,prefix_to_test):
        results = list()
        for entry in prefix_list:
            if self.is_matching_prefix(prefix_to_test,entry['prefix'],entry['masklength_range']):
                results.append(entry)
        return results

    def filter_pyats_ios_pfx_list(self,pyats_prefix_list):

        final_prefix_list = dict()

        for pfx_list in pyats_prefix_list['prefix_set_name']:

            pfx_list_entries = list()

            for _ , pfx_entry in pyats_prefix_list['prefix_set_name'][pfx_list]['prefixes'].items():
                entry = dict()
                entry['prefix'] = pfx_entry['prefix']
                entry['masklength_range'] = pfx_entry['masklength_range']
                pfx_list_entries.append(entry)

            final_prefix_list[pfx_list] = pfx_list_entries
        
        return final_prefix_list

