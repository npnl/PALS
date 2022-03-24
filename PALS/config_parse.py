import json
import os


class PALSConfig():
    def __init__(self,
                 config_path: str):
        '''
        Creates the PALSConfig object with the entries specified in the input JSON file.
        Parameters
        ----------
        config_path : str
            Path to the JSON file containing the desired processing parameters.
        '''
        # Load config file
        f = open(config_path, 'r')
        self.__dict__ = json.load(f)
        f.close()

        # Parse additional values
        self.substitute_empty_outputs()

        # Registration + space- entity
        self.space_entity()
        return

    def __getitem__(self, item):
        return self.__dict__[item]

    def __setitem__(self, key, value):
        self.__dict__[key] = value
        return

    def substitute_empty_outputs(self):
        '''
        Checks for empty values in the "Outputs" dictionary and replaces them with "Root".
        Returns
        -------
        None
        '''
        # If Root is empty, set to CWD
        if(len(self['Outputs']['Root']) == 0):
            self['Outputs']['Root'] = os.path.curdir

        # Iterate through entries in 'Outputs'; set to Root if empty
        for k, v in self['Outputs'].items():
            if(len(v) == 0):
                self['Outputs'][k] = self['Outputs']['Root']
        return

    def space_entity(self):
        '''
        Makes the config entry 'OutputRegistrationSpace' consistent with the analysis settings.
        Returns
        -------
        None
        '''
        if(self['Analysis']['Registration']):
            if(len(self['Outputs']['OutputRegistrationSpace']) == 0):
                raise ValueError("Error in config file; config['Outputs']['OutputRegistrationSpace'] must be defined.")
        else:
            self['Outputs']['OutputRegistrationSpace'] = self['Outputs']['StartRegistrationSpace']
        return