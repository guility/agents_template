package application

import "context"

// RepositoryPort defines the interface for repository implementations
type RepositoryPort[T any] interface {
	GetByID(ctx context.Context, id string) (*T, error)
	GetAll(ctx context.Context) ([]*T, error)
	Save(ctx context.Context, entity *T) error
	Delete(ctx context.Context, id string) error
	FindWhere(ctx context.Context, criteria map[string]interface{}) ([]*T, error)
}

// UseCase defines the interface for application use cases
type UseCase interface {
	Execute(ctx context.Context, request interface{}) (interface{}, error)
	Validate(request interface{}) error
}
