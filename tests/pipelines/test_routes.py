import io
from unittest.mock import patch

from app.constants import (
    AUTH_HOSTNAME,
)
from application_roles.services import create_application
from app.utils import ApplicationsEnum
import responses
from app.constants import WORKFLOW_HOSTNAME
from app.pipelines.models import OrganizationPipeline, OrganizationPipelineRun, db
from app.pipelines.queries import find_organization_pipelines
from application_roles.decorators import ROLES_KEY
from requests import HTTPError

from ..conftest import (
    JWT_TOKEN,
    ORGANIZATION_UUID,
    USER_UUID,
    PIPELINE_UUID,
    PIPELINE_RUN_UUID,
)
from .test_services import (
    PIPELINE_JSON,
    PIPELINE_RUN_JSON,
    PIPELINE_RUN_RESPONSE_JSON,
)


def test_requests_have_cors(app, client, client_application):
    result = client.get(
        f"/v1/organizations/{ORGANIZATION_UUID}/pipelines",
        content_type="application/json",
    )
    assert result.headers["Access-Control-Allow-Origin"] == "*"


def test_pipelines_no_roles_provided(app, client, client_application):
    result = client.get(
        f"/v1/organizations/{ORGANIZATION_UUID}/pipelines",
        content_type="application/json",
    )
    assert result.status_code == 401

    result = client.get(
        f"/v1/organizations/{ORGANIZATION_UUID}/pipelines",
        content_type="application/json",
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
        },
    )
    assert result.status_code == 401


@responses.activate
def test_pipelines_backing_error(app, client, client_application):
    responses.add(
        responses.POST,
        f"{app.config[WORKFLOW_HOSTNAME]}/v1/pipelines/search",
        status=500,
    )

    result = client.get(
        f"/v1/organizations/{ORGANIZATION_UUID}/pipelines",
        content_type="application/json",
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )
    assert result.status_code == 503


@responses.activate
def test_pipelines_bad_search(app, client, client_application):
    json_response = {
        "errors": {"uuids": {"0": ["String does not match expected pattern."]}},
        "message": "Unable to search pipeline",
    }
    responses.add(
        responses.POST,
        f"{app.config[WORKFLOW_HOSTNAME]}/v1/pipelines/search",
        json=json_response,
        status=400,
    )

    result = client.get(
        f"/v1/organizations/{ORGANIZATION_UUID}/pipelines",
        content_type="application/json",
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )
    assert result.status_code == 400
    assert result.json == json_response


@responses.activate
def test_pipelines(app, client, client_application, organization_pipeline):
    pipeline_json = dict(PIPELINE_JSON)
    pipeline_json.update(
        {
            "created_at": "2020-10-08T12:20:36.564095",
            "updated_at": "2020-10-08T12:20:36.564100",
            "uuid": organization_pipeline.pipeline_uuid,
        }
    )
    json_response = [pipeline_json]
    responses.add(
        responses.POST,
        f"{app.config[WORKFLOW_HOSTNAME]}/v1/pipelines/search",
        json=json_response,
    )

    result = client.get(
        f"/v1/organizations/{ORGANIZATION_UUID}/pipelines",
        content_type="application/json",
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )
    assert result.status_code == 200
    json_response[0]["uuid"] = organization_pipeline.uuid
    assert result.json == json_response


@patch("app.pipelines.routes.create_pipeline")
@responses.activate
def test_create_pipeline_backend_500(
    create_pipeline_mock, app, client, client_application
):
    create_pipeline_mock.side_effect = HTTPError("something is wrong")
    result = client.post(
        f"/v1/organizations/{ORGANIZATION_UUID}/pipelines",
        content_type="application/json",
        json=PIPELINE_JSON,
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )
    assert result.status_code == 503
    assert result.json == {"message": "something is wrong"}


@patch("app.pipelines.routes.create_pipeline")
@responses.activate
def test_create_pipeline_backend_error(
    create_pipeline_mock, app, client, client_application
):
    message = {"message": "error"}
    create_pipeline_mock.side_effect = ValueError(message)
    result = client.post(
        f"/v1/organizations/{ORGANIZATION_UUID}/pipelines",
        content_type="application/json",
        json=PIPELINE_JSON,
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )
    assert result.status_code == 400
    assert result.json == message


@responses.activate
def test_create_pipeline(app, client, client_application):
    json_response = dict(PIPELINE_JSON)
    json_response.update(
        {
            "created_at": "2020-10-08T12:20:36.564095",
            "updated_at": "2020-10-08T12:20:36.564100",
            "uuid": "daf6febec1714ac79a73327760c89f15",
        }
    )
    responses.add(
        responses.POST,
        f"{app.config[WORKFLOW_HOSTNAME]}/v1/pipelines",
        json=json_response,
    )

    result = client.post(
        f"/v1/organizations/{ORGANIZATION_UUID}/pipelines",
        content_type="application/json",
        json=PIPELINE_JSON,
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )
    assert result.status_code == 200

    pipeline = OrganizationPipeline.query.order_by(
        OrganizationPipeline.id.desc()
    ).first()
    json_response["uuid"] = pipeline.uuid
    assert result.json == json_response


@patch("app.pipelines.routes.update_pipeline")
@responses.activate
def test_update_pipeline_backend_500(
    update_pipeline_mock, app, client, client_application
):
    update_pipeline_mock.side_effect = HTTPError("something is wrong")
    result = client.put(
        f"/v1/organizations/{ORGANIZATION_UUID}/pipelines/" + "0" * 32,
        content_type="application/json",
        json=PIPELINE_JSON,
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )
    assert result.status_code == 503
    assert result.json == {"message": "something is wrong"}


@patch("app.pipelines.routes.update_pipeline")
@responses.activate
def test_update_pipeline_backend_error(
    update_pipeline_mock, app, client, client_application
):
    message = {"message": "error"}
    update_pipeline_mock.side_effect = ValueError(message)
    result = client.put(
        f"/v1/organizations/{ORGANIZATION_UUID}/pipelines/" + "0" * 32,
        content_type="application/json",
        json=PIPELINE_JSON,
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )
    assert result.status_code == 400
    assert result.json == message


@responses.activate
def test_update_pipeline(app, client, client_application, organization_pipeline):
    json_response = dict(PIPELINE_JSON)
    json_response.update(
        {
            "updated_at": "2020-10-08T12:20:36.564095",
            "updated_at": "2020-10-08T12:20:36.564100",
            "uuid": "daf6febec1714ac79a73327760c89f15",
        }
    )
    responses.add(
        responses.PUT,
        f"{app.config[WORKFLOW_HOSTNAME]}/v1/pipelines/{organization_pipeline.pipeline_uuid}",
        json=json_response,
    )

    result = client.put(
        f"/v1/organizations/{ORGANIZATION_UUID}/pipelines/{organization_pipeline.uuid}",
        content_type="application/json",
        json=PIPELINE_JSON,
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )
    assert result.status_code == 200

    organization_pipeline = OrganizationPipeline.query.order_by(
        OrganizationPipeline.id.desc()
    ).first()
    json_response["uuid"] = organization_pipeline.uuid
    assert result.json == json_response


@responses.activate
def test_delete_pipeline(app, client, client_application, organization_pipeline):
    responses.add(
        responses.DELETE,
        f"{app.config[WORKFLOW_HOSTNAME]}/v1/pipelines/{organization_pipeline.pipeline_uuid}",
    )

    result = client.delete(
        f"/v1/organizations/{ORGANIZATION_UUID}/pipelines/{organization_pipeline.uuid}",
        content_type="application/json",
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )
    assert result.status_code == 200
    assert set(find_organization_pipelines(ORGANIZATION_UUID)) == set()


@patch("app.pipelines.routes.delete_pipeline")
@responses.activate
def test_delete_pipeline_http_error(
    delete_mock, app, client, client_application, organization_pipeline
):
    delete_mock.side_effect = HTTPError("something is wrong")
    result = client.delete(
        f"/v1/organizations/{ORGANIZATION_UUID}/pipelines/{organization_pipeline.uuid}",
        content_type="application/json",
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )
    assert result.status_code == 503
    assert set(find_organization_pipelines(ORGANIZATION_UUID)) == set(
        [organization_pipeline]
    )
    assert result.json == {"message": "something is wrong"}


@patch("app.pipelines.routes.delete_pipeline")
@responses.activate
def test_delete_pipeline_bad_response(
    delete_mock, app, client, client_application, organization_pipeline
):
    message = {"message": "error"}
    delete_mock.side_effect = ValueError(message)
    result = client.delete(
        f"/v1/organizations/{ORGANIZATION_UUID}/pipelines/{organization_pipeline.uuid}",
        content_type="application/json",
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )
    assert result.status_code == 400
    assert set(find_organization_pipelines(ORGANIZATION_UUID)) == set(
        [organization_pipeline]
    )


@responses.activate
def test_upload_input_file_bad_data(app, client, organization_pipeline):
    application = create_application("test client", ApplicationsEnum.REACT_CLIENT)

    db.session.add(application)
    db.session.commit()

    responses.add(
        responses.GET,
        f"{app.config[AUTH_HOSTNAME]}/users/{USER_UUID}/organizations",
        body="not json",
    )

    result = client.post(
        f"/v1/organizations/{ORGANIZATION_UUID}/pipelines/{organization_pipeline.uuid}/input_files",
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: application.api_key,
        },
        data=io.BytesIO(b"some data"),
    )
    assert result.status_code == 401
    assert len(organization_pipeline.organization_pipeline_input_files) == 0


@responses.activate
def test_upload_input_file_no_org(
    app, client, client_application, organization_pipeline
):
    result = client.post(
        f"/v1/organizations/{ORGANIZATION_UUID}/pipelines/nouuid/input_files",
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
        data=b"some data",
    )
    assert result.status_code == 400
    assert len(organization_pipeline.organization_pipeline_input_files) == 0


@responses.activate
def test_upload_input_file_invalid_args(
    app, client, client_application, organization_pipeline
):
    result = client.post(
        f"/v1/organizations/{ORGANIZATION_UUID}/pipelines/{organization_pipeline.uuid}/input_files",
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
        data=b"some data",
    )
    assert result.status_code == 400
    assert len(organization_pipeline.organization_pipeline_input_files) == 0


@patch("app.pipelines.services.upload_stream")
@responses.activate
def test_upload_input_file_value_error(
    upload_stream_mock, app, client, client_application, organization_pipeline
):
    upload_stream_mock.side_effect = ValueError("blah")
    result = client.post(
        f"/v1/organizations/{ORGANIZATION_UUID}/pipelines/{organization_pipeline.uuid}/input_files?name=afile.txt",
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
        data=b"some data",
    )
    assert result.status_code == 400
    assert len(organization_pipeline.organization_pipeline_input_files) == 0


@patch("app.pipelines.services.upload_stream")
@responses.activate
def test_upload_input_file_http_error(
    upload_stream_mock, app, client, client_application, organization_pipeline
):
    upload_stream_mock.side_effect = HTTPError("err")
    result = client.post(
        f"/v1/organizations/{ORGANIZATION_UUID}/pipelines/{organization_pipeline.uuid}/input_files?name=afile.txt",
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
        data=b"some data",
    )
    assert result.status_code == 503
    assert len(organization_pipeline.organization_pipeline_input_files) == 0


@patch("app.pipelines.services.upload_stream")
@responses.activate
def test_upload_input_file(
    upload_stream_mock, app, client, client_application, organization_pipeline
):
    result = client.post(
        f"/v1/organizations/{ORGANIZATION_UUID}/pipelines/{organization_pipeline.uuid}/input_files?name=afile.txt",
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
        data=b"some data",
    )
    assert result.status_code == 200
    assert len(organization_pipeline.organization_pipeline_input_files) == 1

@responses.activate
def test_create_pipeline_run(app, client, client_application, organization_pipeline):
    json_response = dict(PIPELINE_RUN_RESPONSE_JSON)

    pipeline = OrganizationPipeline.query.order_by(
        OrganizationPipeline.id.desc()
    ).first()

    responses.add(
        responses.POST,
        f"{app.config[WORKFLOW_HOSTNAME]}/v1/pipelines/{pipeline.pipeline_uuid}/runs",
        json=json_response,
    )

    result = client.post(
        f"/v1/organizations/{pipeline.organization_uuid}/pipelines/{pipeline.uuid}/runs",
        content_type="application/json",
        json=PIPELINE_RUN_JSON,
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )
    resp = result.json
    new_run = OrganizationPipelineRun.query.filter(
        OrganizationPipelineRun.pipeline_run_uuid == resp["uuid"]
    ).first()

    assert result.status_code == 200
    assert new_run is not None
    assert result.json == json_response


@patch("app.pipelines.routes.create_pipeline_run")
@responses.activate
def test_create_pipeline_run_value_error(
    mock_create, app, client, client_application, organization_pipeline
):
    mock_create.side_effect = ValueError("error")

    result = client.post(
        f"/v1/organizations/{organization_pipeline.organization_uuid}/pipelines/{organization_pipeline.uuid}/runs",
        content_type="application/json",
        json={"some": "json"},
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )

    assert result.status_code == 400


@patch("app.pipelines.routes.create_pipeline_run")
@responses.activate
def test_create_pipeline_run_http_error(
    mock_create, app, client, client_application, organization_pipeline
):
    json_response = dict(PIPELINE_RUN_RESPONSE_JSON)

    mock_create.side_effect = HTTPError("error")

    result = client.post(
        f"/v1/organizations/{organization_pipeline.organization_uuid}/pipelines/{organization_pipeline.uuid}/runs",
        content_type="application/json",
        json={"some": "json"},
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )

    assert result.status_code == 503


@responses.activate
def test_list_pipeline_runs(app, client, client_application, organization_pipeline):
    json_response = [PIPELINE_RUN_RESPONSE_JSON]

    pipeline = OrganizationPipeline.query.order_by(
        OrganizationPipeline.id.desc()
    ).first()

    responses.add(
        responses.GET,
        f"{app.config[WORKFLOW_HOSTNAME]}/v1/pipelines/{pipeline.pipeline_uuid}/runs",
        json=json_response,
    )

    result = client.get(
        f"/v1/organizations/{pipeline.organization_uuid}/pipelines/{pipeline.uuid}/runs",
        content_type="application/json",
        json=PIPELINE_RUN_JSON,
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )
    resp = result.json

    assert result.status_code == 200
    assert result.json == json_response


@responses.activate
def test_list_pipeline_runs(app, client, client_application, organization_pipeline):
    json_response = [PIPELINE_RUN_RESPONSE_JSON]

    pipeline = OrganizationPipeline.query.order_by(
        OrganizationPipeline.id.desc()
    ).first()

    responses.add(
        responses.GET,
        f"{app.config[WORKFLOW_HOSTNAME]}/v1/pipelines/{pipeline.pipeline_uuid}/runs",
        json=json_response,
    )

    result = client.get(
        f"/v1/organizations/{pipeline.organization_uuid}/pipelines/{pipeline.uuid}/runs",
        content_type="application/json",
        json=PIPELINE_RUN_JSON,
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )
    resp = result.json

    assert result.status_code == 200
    assert result.json == json_response


@patch("app.pipelines.routes.fetch_pipeline_runs")
@patch("flask.jsonify")
@responses.activate
def test_list_pipeline_runs_value_error(
    mock_fetch, mock_jsonify, app, client, client_application, organization_pipeline
):
    mock_fetch.side_effect = {"some": "json"}
    mock_jsonify.side_effect = ValueError("error")

    result = client.get(
        f"/v1/organizations/{organization_pipeline.organization_uuid}/pipelines/{organization_pipeline.uuid}/runs",
        content_type="application/json",
        json=PIPELINE_RUN_JSON,
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )

    assert result.status_code == 400
    assert mock_jsonify.called is True


@patch("app.pipelines.routes.fetch_pipeline_runs")
@responses.activate
def test_list_pipeline_runs_http_error(
    mock_fetch, app, client, client_application, organization_pipeline
):
    mock_fetch.side_effect = HTTPError("error")

    result = client.get(
        f"/v1/organizations/{organization_pipeline.organization_uuid}/pipelines/{organization_pipeline.uuid}/runs",
        content_type="application/json",
        json=PIPELINE_RUN_JSON,
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )

    assert result.status_code == 503


@responses.activate
def test_pipeline_run(
    app, client, client_application, organization_pipeline, organization_pipeline_run
):
    json_response = dict(PIPELINE_RUN_RESPONSE_JSON)

    pipeline = OrganizationPipeline.query.order_by(
        OrganizationPipeline.id.desc()
    ).first()

    pipeline_run = pipeline.organization_pipeline_runs[0]

    responses.add(
        responses.GET,
        f"{app.config[WORKFLOW_HOSTNAME]}/v1/pipelines/{pipeline.pipeline_uuid}/runs/{pipeline_run.pipeline_run_uuid}",
        json=json_response,
    )

    result = client.get(
        f"/v1/organizations/{pipeline.organization_uuid}/pipelines/{pipeline.uuid}/runs/{pipeline_run.uuid}",
        content_type="application/json",
        json=PIPELINE_RUN_JSON,
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )
    resp = result.json

    assert result.status_code == 200
    assert result.json == json_response

@patch("app.pipelines.routes.fetch_pipeline_run")
@patch("flask.jsonify")
@responses.activate
def test_list_pipeline_run_value_error(
    mock_fetch,
    mock_jsonify,
    app,
    client,
    client_application,
    organization_pipeline,
    organization_pipeline_run,
):
    mock_fetch.side_effect = {"some": "json"}
    mock_jsonify.side_effect = ValueError("error")

    pipeline = OrganizationPipeline.query.order_by(
        OrganizationPipeline.id.desc()
    ).first()
    pipeline_run = pipeline.organization_pipeline_runs[0]

    result = client.get(
        f"/v1/organizations/{pipeline.organization_uuid}/pipelines/{pipeline.uuid}/runs/{pipeline_run.uuid}",
        content_type="application/json",
        json=PIPELINE_RUN_JSON,
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )

    assert result.status_code == 400
    assert mock_jsonify.called is True


@patch("app.pipelines.routes.fetch_pipeline_run")
@responses.activate
def test_list_pipeline_run_http_error(
    mock_fetch,
    app,
    client,
    client_application,
    organization_pipeline,
    organization_pipeline_run,
):
    mock_fetch.side_effect = HTTPError("error")

    pipeline = OrganizationPipeline.query.order_by(
        OrganizationPipeline.id.desc()
    ).first()
    pipeline_run = pipeline.organization_pipeline_runs[0]

    result = client.get(
        f"/v1/organizations/{pipeline.organization_uuid}/pipelines/{pipeline.uuid}/runs/{pipeline_run.uuid}",
        content_type="application/json",
        json=PIPELINE_RUN_JSON,
        headers={
            "Authorization": f"Bearer {JWT_TOKEN}",
            ROLES_KEY: client_application.api_key,
        },
    )

    assert result.status_code == 503
