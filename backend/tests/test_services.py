from app.services.email_service import send_password_reset_email

def test_email_service_no_api_key(app, mocker):
    app.config['SENDGRID_API_KEY'] = None
    mocker.patch('os.environ.get', return_value=None)
    mocker.patch('flask.current_app.logger.error')
    assert not send_password_reset_email('test@test.com', 'link')

def test_email_service_sendgrid_api_error(app, mocker):
    app.config['SENDGRID_API_KEY'] = 'dummy-key'
    mock_client = mocker.patch('app.services.email_service.SendGridAPIClient')
    mock_instance = mock_client.return_value
    mock_instance.send.side_effect = Exception("API Error")
    mocker.patch('flask.current_app.logger.error')
    assert not send_password_reset_email('test@test.com', 'link')

def test_email_service_success_path(app, mocker):
    app.config['SENDGRID_API_KEY'] = 'dummy-key'
    mock_response = mocker.Mock()
    mock_response.status_code = 202
    mock_client = mocker.patch('app.services.email_service.SendGridAPIClient')
    mock_instance = mock_client.return_value
    mock_instance.send.return_value = mock_response
    mock_logger = mocker.patch('flask.current_app.logger.info')

    result = send_password_reset_email('test@test.com', 'link')
    
    assert result is True
    mock_instance.send.assert_called_once()
    mock_logger.assert_called_once()
