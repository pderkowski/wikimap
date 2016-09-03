import logging
import Utils

class Dictionary(object):
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.id2title = {}
        self.title2id = {}

    def save(self, output):
        output = Utils.openOrExit(output, 'w')
        Dictionary.logger.info('Started saving a dictionary.')
        for id, title in self.id2title.iteritems():
            output.write('{} {}\n'.format(id, title))

        Dictionary.logger.info('Finished saving a dictionary.')
        output.close()

    def load(self, input):
        input = Utils.openOrExit(input, 'r')
        Dictionary.logger.info('Started loading the dictionary.')
        for i, l in enumerate(input):
            if i % 1000000 == 0:
                Dictionary.logger.info('Loaded {} records'.format(i))

            parts = l.rstrip().split()
            if len(parts) == 2:
                id = int(parts[0])
                title = parts[1]
                self.id2title[id] = title
                self.title2id[title] = id
            else:
                Dictionary.logger.warn('Line {}:{} does not have 2 values.'.format(i, l.rstrip()))

        Dictionary.logger.info('Finished loading the dictionary.')
        input.close()