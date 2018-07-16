import logging
from pathlib import Path

from xmltodict import parse

from helpers.git_cli_client import GitCliClient, GIT_TEMP_DIRECTORY
from helpers.kdiff3 import KDiff3
from helpers.requests import response, check_args_have
from models.data_model import DB_SESSION, DB_S2
from models.file import update_assignee, File
from models.session import transform_file
from models.user import User
from templates.mail.files import file_assigned

logger = logging.getLogger(__name__)


def assign_file(kwargs):
    """
    Assigns a file to a user
    """

    # Todo: add authorization

    required_args = ['logged_user', 'session_id', 'file_id', 'user_id']
    if not check_args_have(kwargs, required_args):
        return response(400, 'Invalid input')

    DB_SESSION.commit() // make a DB commit

    try:
        if update_assignee(kwargs['logged_user'], kwargs['session_id'],
                           kwargs['file_id'], kwargs['user_id']):
            file = DB_SESSION.query(File).filter(File.id == kwargs['file_id']).one()

            file_assigned(file)
            return response(200, 'OK')
        return response(401, 'Not permitted')
    except Exception as identifier:
        logger.error('Can not assign users within the database')
        print(identifier)
        return response(500, 'Error has occurred while assigning the file')



def xml_to_json(xml_content):
    try:
        arr = parse(xml_content)

    except Exception as e:
        print('error converting from XML to dict')
        print(str(e))
        return False

    return arr


def show(file_id, session_id, kwargs):
    """
    This function will show the conflicted file and it's details (code diff, conflicts)

    :param file_id:
    :param session_id:
    :param kwargs:
    :return:
    """
    DB_SESSION.commit() # to avoid caching

    # Todo: add authorization
    from models.session import Session
    record = DB_SESSION.query(File, Session, User) \
        .join(Session) \
        .outerjoin(User, File.assignee_id == User.id) \
        .filter(File.id == file_id) \
        .filter(File.session_id == session_id) \
        .one()

    if not record:
        return response(404, "Not found")

    file = record[0]
    session = record[1]
    assignee = record[2]

    # get sources
    base_commit_id = GitCliClient.get_base_commit(session)
    base_commit_id = base_commit_id.decode().rstrip()

    temp_directory = session.containing_dir + "/" + GIT_TEMP_DIRECTORY + "/"
    new_output_file = temp_directory + file.relative_path + "_A"
    a = GitCliClient.get_base_file(session, base_commit_id, file.relative_path, new_output_file)

    # run KDiff3
    kdiff_postfix = KDiff3.run(a, b, c, output_path)
    kdiff_content = KDiff3.get_content(output_path)
    diff_dictionary = xml_to_json(kdiff_content)

    if not kdiff_postfix or not diff_dictionary or not kdiff_content:
        return response(500, "Internal server error")

    result = {
        'file': transform_file(file, assignee),
        'base_commit_id': base_commit_id,
        'A': a,
        'B': b,
        'C': c,
        'output': output_path,
        'postfix': kdiff_postfix,
        'diff': diff_dictionary
    }
    return response(200, 'OK', result)


def handle_get_merge_sessions(kwargs):
    """
    Handles {GET} merge_sessions/... requests
    """
    # GET: /merge_sessions
    if not kwargs['nested'] or not len(kwargs['nested']):
        return index(kwargs)

    # GET: /merge_sessions/{session_id}
    if len(kwargs['nested']) == 1 and \
            isInt(kwargs['nested'][0]):
        kwargs['session_id'] = int(kwargs['nested'][0])
        return show(kwargs)

    # Handles {GET} merge_sessions/{id}/file/{id}
    if (len(kwargs['nested']) == 3 and
            isInt(kwargs['nested'][0]) and
            kwargs['nested'][1] == 'files'):
        kwargs['session_id'] = int(kwargs['nested'][0])
        kwargs['file_id'] = int(kwargs['nested'][2])

        return controllers._file.show(kwargs['file_id'], kwargs['session_id'], kwargs)

    # Handles {GET} merge_sessions/{id}/logs/
    if (len(kwargs['nested']) == 2 and
            isInt(kwargs['nested'][0]) and
            kwargs['nested'][1] == 'logs'):
        kwargs['session_id'] = int(kwargs['nested'][0])
        return controllers._session.logs(kwargs)

    # # GET: /merge_sessions/assignments
    # if len(kwargs['nested']) == 1 and\
    #    kwargs['nested'][0] == 'assignments':
    #     return query_my_assignments(kwargs)
    return handle_invalid_request(kwargs)

