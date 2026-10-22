package domain

import "time"

// BaseEntity represents common fields for all domain entities
type BaseEntity struct {
	ID        string    `json:"id"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// Entity defines the interface for all domain entities
type Entity interface {
	GetID() string
	GetCreatedAt() time.Time
	GetUpdatedAt() time.Time
	Validate() error
}

// ValueObject defines the interface for value objects in DDD
type ValueObject interface {
	Equals(other ValueObject) bool
	Validate() error
}
