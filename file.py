import logging

from xmltodict import parse

from helpers.git_cli_client import GitCliClient, GIT_TEMP_DIRECTORY
from helpers.requests import response, check_args_have
from models.data_model import DB_SESSION
from models.file import update_assignee, File
from models.session import transform_file
from models.user import User

logger = logging.getLogger(__name__)


def handle_get_users(kwargs):
    """
    Handles {GET} merge_sessions/... requests
    """
    # GET: /users
    if not kwargs['nested'] or not len(kwargs['nested']):
        return controllers._user.index(kwargs)

    # GET: /users/{user_id}
    if len(kwargs['nested']) == 1 and \
            isInt(kwargs['nested'][0]):
        kwargs['user_id'] = int(kwargs['nested'][0])
        return controllers._user.show(kwargs)

    # # GET: /merge_sessions/assignments
    # if len(kwargs['nested']) == 1 and\
    #    kwargs['nested'][0] == 'assignments':
    #     return query_my_assignments(kwargs)
    return handle_invalid_request(kwargs)


def assign_file(kwargs):
    """
    Assigns a file to a user
    """

    DB_SESSION.commit()

    try:
        print(kwargs)
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

    base_commit_id = GitCliClient.get_base_commit(session)
    base_commit_id = base_commit_id.decode().rstrip()

    if not a:  # file didn't exist in base branch!
        a = new_output_file
        Path(a).touch()

    b = GitCliClient.get_show_file(
        session, "from", session.from_branch_name, file.relative_path, "B")
    c = GitCliClient.get_show_file(
        session, "to", session.to_branch_name, file.relative_path, "C")
    output_path = session.containing_dir + "/" + \
                  GIT_TEMP_DIRECTORY + "/" + file.relative_path + ".xml"

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



