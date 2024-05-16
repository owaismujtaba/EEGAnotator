import pyxdf


class XDFDATA:
    def __init__(self, filepath) -> None:
        self.filepath = filepath
        self.filname = self.filepath.split('/')[-1]
        self.streams = None
        self.n_channels = []
        self.channel_types = []
        self.channel_names = []    

    def load_xdf_file(self):
        print('Loading {} file', self.filepath.split('/')[-1])
        self.streams, _ = pyxdf.load_xdf(self.filepath)

    def file_info(self):
        ####### Information about the Recordings ######
        self.n_channels = len(self.streams)

        for channel_no in range(self.n_channels):
            channel_data = self.streams[channel_no]
            self.channel_names.append(channel_data[channel_no]['info']['name'][0])
            self.channel_types.append(channel_data[channel_no]['info']['type'][0])
