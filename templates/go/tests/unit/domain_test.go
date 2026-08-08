package domain_test

import (
	"testing"
	"time"

	"github.com/example/ddd-go-project/src/domain"
)

func TestBaseEntity_Creation(t *testing.T) {
	entity := domain.BaseEntity{
		ID: "test-id",
	}

	if entity.ID != "test-id" {
		t.Errorf("Expected ID 'test-id', got '%s'", entity.ID)
	}

	if entity.CreatedAt.IsZero() {
		t.Error("CreatedAt should not be zero")
	}

	if entity.UpdatedAt.IsZero() {
		t.Error("UpdatedAt should not be zero")
	}
}

func TestBaseEntity_Timestamps(t *testing.T) {
	before := time.Now()
	entity := domain.BaseEntity{ID: "test"}
	after := time.Now()

	if entity.CreatedAt.Before(before) || entity.CreatedAt.After(after) {
		t.Error("CreatedAt should be within expected range")
	}

	if entity.UpdatedAt.Before(before) || entity.UpdatedAt.After(after) {
		t.Error("UpdatedAt should be within expected range")
	}
}
