package handler

import (
	"encoding/json"
	"net/http"
)

// ResponseDTO represents a standard API response
type ResponseDTO struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
}

// RequestDTO represents a standard API request
type RequestDTO struct {
	ID     string                 `json:"id,omitempty"`
	Params map[string]interface{} `json:"params,omitempty"`
}

// WriteJSON writes a JSON response
func WriteJSON(w http.ResponseWriter, statusCode int, data interface{}) error {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	return json.NewEncoder(w).Encode(data)
}

// WriteError writes an error response
func WriteError(w http.ResponseWriter, statusCode int, message string) error {
	response := ResponseDTO{
		Success: false,
		Error:   message,
	}
	return WriteJSON(w, statusCode, response)
}

// WriteSuccess writes a success response
func WriteSuccess(w http.ResponseWriter, data interface{}) error {
	response := ResponseDTO{
		Success: true,
		Data:    data,
	}
	return WriteJSON(w, http.StatusOK, response)
}
