"""
Unit tests for centralized response helpers
"""

import pytest
from datetime import datetime
from backend.utils.responses import (
    create_standardized_response,
    create_error_response,
    create_validation_error_response
)

class TestResponseHelpers:
    """Test cases for response helper functions"""
    
    def test_create_standardized_response_basic(self):
        """Test create_standardized_response with basic data"""
        data = {"message": "success"}
        response = create_standardized_response(data)
        
        # Check structure
        assert "data" in response
        assert "meta" in response
        assert "errors" in response
        
        # Check data
        assert response["data"] == data
        
        # Check meta structure
        meta = response["meta"]
        assert "timestamp" in meta
        assert "request_id" in meta
        assert "status_code" in meta
        
        # Check values
        assert meta["status_code"] == 200
        assert isinstance(meta["request_id"], str)
        assert isinstance(meta["timestamp"], str)
        
        # Check errors
        assert response["errors"] == []
    
    def test_create_standardized_response_with_custom_status(self):
        """Test create_standardized_response with custom status code"""
        data = {"created": True}
        response = create_standardized_response(data, status_code=201)
        
        assert response["meta"]["status_code"] == 201
        assert response["data"] == data
    
    def test_create_standardized_response_with_message(self):
        """Test create_standardized_response with optional message"""
        data = {"result": "ok"}
        message = "Operation completed successfully"
        response = create_standardized_response(data, message=message)
        
        # Message is not currently stored in response, but function accepts it
        assert response["data"] == data
        assert response["meta"]["status_code"] == 200
    
    def test_create_error_response_basic(self):
        """Test create_error_response with basic error"""
        code = "VALIDATION_ERROR"
        message = "Invalid input data"
        response = create_error_response(code, message)
        
        # Check structure
        assert "data" in response
        assert "meta" in response
        assert "errors" in response
        
        # Check data is null
        assert response["data"] is None
        
        # Check meta structure
        meta = response["meta"]
        assert "timestamp" in meta
        assert "request_id" in meta
        assert "status_code" in meta
        
        # Check values
        assert meta["status_code"] == 400
        assert isinstance(meta["request_id"], str)
        assert isinstance(meta["timestamp"], str)
        
        # Check errors
        assert len(response["errors"]) == 1
        error = response["errors"][0]
        assert error["code"] == code
        assert error["message"] == message
        assert "field" not in error
        assert "details" not in error
    
    def test_create_error_response_with_field(self):
        """Test create_error_response with field specification"""
        code = "FIELD_ERROR"
        message = "Field is required"
        field = "username"
        response = create_error_response(code, message, field=field)
        
        error = response["errors"][0]
        assert error["field"] == field
        assert error["code"] == code
        assert error["message"] == message
    
    def test_create_error_response_with_details(self):
        """Test create_error_response with additional details"""
        code = "PROCESSING_ERROR"
        message = "Failed to process request"
        details = {"attempts": 3, "last_error": "timeout"}
        response = create_error_response(code, message, details=details)
        
        error = response["errors"][0]
        assert error["details"] == details
        assert error["code"] == code
        assert error["message"] == message
    
    def test_create_error_response_with_custom_status(self):
        """Test create_error_response with custom status code"""
        code = "NOT_FOUND"
        message = "Resource not found"
        response = create_error_response(code, message, status_code=404)
        
        assert response["meta"]["status_code"] == 404
        assert response["errors"][0]["code"] == code
    
    def test_create_error_response_with_all_parameters(self):
        """Test create_error_response with all optional parameters"""
        code = "COMPLEX_ERROR"
        message = "Multiple validation failures"
        field = "email"
        details = {"format": "invalid", "suggestion": "user@domain.com"}
        status_code = 422
        
        response = create_error_response(code, message, field, details, status_code)
        
        # Check meta
        assert response["meta"]["status_code"] == status_code
        
        # Check error
        error = response["errors"][0]
        assert error["code"] == code
        assert error["message"] == message
        assert error["field"] == field
        assert error["details"] == details
    
    def test_create_validation_error_response(self):
        """Test create_validation_error_response with multiple errors"""
        validation_errors = [
            {"code": "REQUIRED", "message": "Field is required", "field": "name"},
            {"code": "INVALID_FORMAT", "message": "Invalid email format", "field": "email"}
        ]
        
        response = create_validation_error_response(validation_errors)
        
        # Check structure
        assert response["data"] is None
        assert response["meta"]["status_code"] == 422
        assert len(response["errors"]) == 2
        
        # Check errors
        assert response["errors"] == validation_errors
    
    def test_create_validation_error_response_with_custom_status(self):
        """Test create_validation_error_response with custom status code"""
        validation_errors = [{"code": "TEST", "message": "Test error"}]
        response = create_validation_error_response(validation_errors, status_code=400)
        
        assert response["meta"]["status_code"] == 400
    
    def test_response_timestamp_format(self):
        """Test that timestamps are in correct ISO format with Z suffix"""
        response = create_standardized_response({"test": "data"})
        timestamp = response["meta"]["timestamp"]
        
        # Should end with Z (UTC timezone indicator)
        assert timestamp.endswith("Z")
        
        # Should be parseable as ISO format
        parsed_time = datetime.fromisoformat(timestamp[:-1])  # Remove Z for parsing
        assert isinstance(parsed_time, datetime)
    
    def test_request_id_uniqueness(self):
        """Test that request IDs are unique across responses"""
        response1 = create_standardized_response({"data1": "value1"})
        response2 = create_standardized_response({"data2": "value2"})
        
        id1 = response1["meta"]["request_id"]
        id2 = response2["meta"]["request_id"]
        
        assert id1 != id2
        assert isinstance(id1, str)
        assert isinstance(id2, str)
        assert len(id1) > 0
        assert len(id2) > 0
