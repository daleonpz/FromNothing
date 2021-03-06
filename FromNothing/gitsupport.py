import subprocess
import requests
import logging
logger = logging.getLogger(__name__)

PIPE = subprocess.PIPE

class GitSupport(object):

    def __init__(self, git_info: dict, prjname: str, clone_type: str):
        self.git = git_info
        self.prjname = prjname
        self.clone_type = clone_type
        self.authors = None
        if 'authors' in git_info:
            self.authors = git_info['authors']

    def init_repo(self):
        process = subprocess.Popen(['git', 'init'], stdout=PIPE, stderr=PIPE)
        stdoutput, stderroutput = process.communicate()
        logger.debug(stdoutput.decode('utf-8'))

    def __create_authors_file(self):
        with open('AUTHORS','w') as f: 
            f.write("AUTHORS:\n")

            if self.authors is not None:
                for i in range(0, len(self.authors['name'])):
                    f.write("* " + self.authors['name'][i] + " ")
                    f.write("("  + self.authors['email'][i] + ")\n")
            else:
                f.write("<Your-Name> <youre_mail> (your_website)")

    def create_info_files(self):
        logger.info("Creating general git files...")
        open('.gitignore', 'a').close()
        open('README', 'a').close()
        open('LICENSE', 'a').close()
        open('CHANGELOG', 'a').close()
        self.__create_authors_file()

    def push_project(self):

        server = self.git['server'] 
        user = self.git['user']
        api_token = self.git['api_token']
        service = self.git['service']

        if service == 'github':
            r = requests.post('https://api.github.com/user/repos', 
                    auth=(user, api_token),
                    json = {"name": self.prjname} )
            logger.info("Request Status :")
            logger.info(r.status_code)

        
        if service == 'gitlab':
            r = requests.post('https://' + server + '/api/v4/projects', 
                    headers={'PRIVATE-TOKEN': api_token},
                    json = {"path": self.prjname + '&namespace_id=' + user} )
            logger.info("Request Status :")
            logger.info(r.status_code)


        process = subprocess.Popen(['git', 'add','--all'], stdout=PIPE, stderr=PIPE)
        stdoutput, stderroutput = process.communicate()
        logger.debug(stdoutput.decode('utf-8'))

        process = subprocess.Popen(['git', 'commit','--m', 'New Project'], stdout=PIPE, stderr=PIPE)
        stdoutput, stderroutput = process.communicate()
        logger.debug(stdoutput.decode('utf-8'))

        gitpath = server + ":" + user + "/" + self.prjname  + '.git'
        
        if self.clone_type == 'ssh':
            gitpath = 'git@' +  gitpath
        else:
            gitpath = 'https://' +  gitpath

        logger.info('GitPath: ' + gitpath)
        process = subprocess.Popen(['git', 'remote', 'add','origin', gitpath], stdout=PIPE, stderr=PIPE)
        stdoutput, stderroutput = process.communicate()
        logger.debug(stdoutput.decode('utf-8'))

        process = subprocess.Popen(['git', 'push','--set-upstream', 'origin', 'master'], stdout=PIPE, stderr=PIPE)
        stdoutput, stderroutput = process.communicate()
        logger.debug(stdoutput.decode('utf-8'))

