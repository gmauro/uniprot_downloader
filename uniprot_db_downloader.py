"""
from a Taxa Id retrieves all the proteins sequences
it returns a multifasta prot file

http://www.crs4.it/
Created by: Gianmauro Cuccuru

python uniprot_db_downloader.py -i "65492;654924" -o test.gz --logfile log
python uniprot_db_downloader.py -i "1507,1772,1752,233413,1063,430066,359391" \
-o test.gz -d 2 -s 2 --no-iso --loglevel DEBUG --logfile log

"""

import sys
import os
import argparse
import logging
import subprocess
import tempfile
import shutil

class Dbfetch:

    def __init__(self, args, logger):
        self.logger = logger
        self.wd = tempfile.mkdtemp()
        self.base = "http://www.uniprot.org/uniprot/"
        self.kb_id = args.kb_id
        self.set_id = args.set_id
        self.taxa_ids = args.taxa_ids
        self.iso = args.iso
        if args.outname:
            self.outname = args.outname
        self.log = args.logfile
        return

    def _execute(self, cmd):
        """ """
        try:
            subprocess.check_call( args=cmd, shell=True, stderr=subprocess.PIPE,
                                   stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            self.logger.error("cmd failed:error %s, %s" % (e, cmd))
            exit(1)

    def run(self):
        """ retrieve fasta files  """
        dbslist = os.path.join(self.wd,'dbslist')
        mfasta_archive = os.path.join(self.wd,'mfasta_archive.gz')
        self.logger.debug("dbslist file %s" % dbslist)

        cmd_args = []

        f = open(dbslist,'w')
        for tid in self.taxa_ids.split(','):
            cmd_args.append("%s?query=(taxonomy:%s)" % (self.base, tid))
            if self.kb_id == 1:
                cmd_args.append("+AND+reviewed:yes")
            if self.kb_id ==  2:
                cmd_args.append("+AND+reviewed:no")
            if self.set_id == 1:
                cmd_args.append("+AND+keyword:1185")
            if self.set_id == 2:
                cmd_args.append("+AND+keyword:181")
            if self.iso:
                cmd_args.append("&include=yes")
            cmd_args.append("&compress=yes&format=fasta\n")
        f.write(''.join(cmd_args))
        f.close()

        cmd = "wget -nv -i %s -O %s -a %s" % (dbslist, mfasta_archive, self.log)
        self.logger.info("Retrieving data from Uniprot for these taxa ids: %s" %
                         self.taxa_ids)
        self.logger.debug("Executing: %s" % cmd)
        self._execute(cmd)
        self._clean_environment(mfasta_archive)
        return

    def _clean_environment(self,archive):
        """ moving and removing files """

        cmd = "gunzip " + archive
        self._execute(cmd)

        self.logger.info("Moving downloaded archive")
        shutil.move(archive.strip('.gz'), self.outname)

        self.logger.debug("Removing temp dir: %s" % self.wd)
        shutil.rmtree(self.wd)
        return

### END OF CLASS

LOG_FORMAT = '%(asctime)s|%(levelname)-8s|%(message)s'
LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'
LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']


def make_parser():
    parser = argparse.ArgumentParser(description='Retrieve data from Uniprot')

    parser.add_argument('-i', dest='taxa_ids', required=True,
                        help='taxa accession ids, mandatory')
    parser.add_argument('-o', type=str, dest='outname', required=True,
                        help='output file name')
    parser.add_argument('-l', '--logfile', type=str, required=True,
                        help='log file')
    parser.add_argument('--loglevel', type=str, choices=LOG_LEVELS,
                        help='logging level (default: INFO)', default='INFO')
    parser.add_argument('-d', type=int, choices=xrange(0, 3), dest='kb_id',
                        help='Protein knowledgebase section name')
    parser.add_argument('-s', type=int, choices=xrange(0, 3), dest='set_id',
                        help='Proteome set name')
    parser.add_argument('--iso',dest='iso',action='store_true',
                        help='Include isoform data')
    return parser


def main():
    """ main function """
    parser = make_parser()
    args = parser.parse_args()

    log_level = getattr(logging, args.loglevel)
    kwargs = {'format'  : LOG_FORMAT,
              'datefmt' : LOG_DATEFMT,
              'level'   : log_level}
    if args.logfile:
        kwargs['filename'] = args.logfile
    logging.basicConfig(**kwargs)
    logger = logging.getLogger('data_from_Uniprot')

    U = Dbfetch(args, logger)
    U.run()
    return


################
if __name__ == "__main__":
    sys.exit(main())
