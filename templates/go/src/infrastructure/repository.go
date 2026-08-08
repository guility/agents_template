package infrastructure

import (
	"context"
	"fmt"
	"sync"
)

// InMemoryRepository is an in-memory implementation of RepositoryPort
type InMemoryRepository[T any] struct {
	data map[string]*T
	mu   sync.RWMutex
}

// NewInMemoryRepository creates a new in-memory repository
func NewInMemoryRepository[T any]() *InMemoryRepository[T] {
	return &InMemoryRepository[T]{
		data: make(map[string]*T),
	}
}

// GetByID retrieves an entity by its ID
func (r *InMemoryRepository[T]) GetByID(ctx context.Context, id string) (*T, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	entity, exists := r.data[id]
	if !exists {
		return nil, fmt.Errorf("entity with id %s not found", id)
	}
	return entity, nil
}

// GetAll retrieves all entities
func (r *InMemoryRepository[T]) GetAll(ctx context.Context) ([]*T, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	result := make([]*T, 0, len(r.data))
	for _, entity := range r.data {
		result = append(result, entity)
	}
	return result, nil
}

// Save persists an entity
func (r *InMemoryRepository[T]) Save(ctx context.Context, entity *T) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	// This assumes T has an ID field - in real implementation you'd use reflection or interface
	r.data[fmt.Sprintf("%v", entity)] = entity
	return nil
}

// Delete removes an entity by ID
func (r *InMemoryRepository[T]) Delete(ctx context.Context, id string) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	if _, exists := r.data[id]; !exists {
		return fmt.Errorf("entity with id %s not found", id)
	}
	delete(r.data, id)
	return nil
}

// FindWhere finds entities matching criteria
func (r *InMemoryRepository[T]) FindWhere(ctx context.Context, criteria map[string]interface{}) ([]*T, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	result := make([]*T, 0)
	for _, entity := range r.data {
		match := true
		for _, value := range criteria {
			// Simplified criteria matching - real implementation would use reflection
			if fmt.Sprintf("%v", entity) != fmt.Sprintf("%v", value) {
				match = false
				break
			}
		}
		if match {
			result = append(result, entity)
		}
	}
	return result, nil
}
