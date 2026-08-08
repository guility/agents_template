namespace DddTemplate.Application;

using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

/// <summary>
/// Repository port interface following Clean Architecture principles
/// </summary>
public interface IRepository<T> where T : class
{
    Task<T?> GetByIdAsync(string id, CancellationToken cancellationToken = default);
    Task<IEnumerable<T>> GetAllAsync(CancellationToken cancellationToken = default);
    Task<T> AddAsync(T entity, CancellationToken cancellationToken = default);
    Task UpdateAsync(T entity, CancellationToken cancellationToken = default);
    Task DeleteAsync(string id, CancellationToken cancellationToken = default);
    Task<IEnumerable<T>> FindWhereAsync(Func<T, bool> predicate, CancellationToken cancellationToken = default);
}

/// <summary>
/// Use case interface for application layer operations
/// </summary>
public interface IUseCase<TRequest, TResponse>
{
    Task<TResponse> ExecuteAsync(TRequest request, CancellationToken cancellationToken = default);
}

/// <summary>
/// Domain event interface for event-driven architecture
/// </summary>
public interface IDomainEvent
{
    string EventId { get; }
    DateTime OccurredOn { get; }
    string AggregateId { get; }
}

/// <summary>
/// Event dispatcher for domain events
/// </summary>
public interface IEventDispatcher
{
    Task DispatchAsync(IDomainEvent domainEvent, CancellationToken cancellationToken = default);
}
