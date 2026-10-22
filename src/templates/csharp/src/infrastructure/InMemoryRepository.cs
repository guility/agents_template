namespace DddTemplate.Infrastructure;

using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using DddTemplate.Application;

/// <summary>
/// In-memory repository implementation for testing and development
/// </summary>
public class InMemoryRepository<T> : IRepository<T> where T : class
{
    private readonly ConcurrentDictionary<string, T> _storage = new();

    public Task<T?> GetByIdAsync(string id, CancellationToken cancellationToken = default)
    {
        _storage.TryGetValue(id, out var entity);
        return Task.FromResult(entity);
    }

    public Task<IEnumerable<T>> GetAllAsync(CancellationToken cancellationToken = default)
    {
        return Task.FromResult<IEnumerable<T>>(_storage.Values);
    }

    public Task<T> AddAsync(T entity, CancellationToken cancellationToken = default)
    {
        var idProperty = entity.GetType().GetProperty("Id");
        var id = idProperty?.GetValue(entity)?.ToString() ?? Guid.NewGuid().ToString();
        
        if (_storage.TryAdd(id, entity))
        {
            return Task.FromResult(entity);
        }
        
        throw new InvalidOperationException($"Entity with id {id} already exists");
    }

    public Task UpdateAsync(T entity, CancellationToken cancellationToken = default)
    {
        var idProperty = entity.GetType().GetProperty("Id");
        var id = idProperty?.GetValue(entity)?.ToString();
        
        if (string.IsNullOrEmpty(id))
        {
            throw new InvalidOperationException("Entity must have an Id");
        }
        
        if (!_storage.ContainsKey(id))
        {
            throw new KeyNotFoundException($"Entity with id {id} not found");
        }
        
        _storage[id] = entity;
        return Task.CompletedTask;
    }

    public Task DeleteAsync(string id, CancellationToken cancellationToken = default)
    {
        if (!_storage.TryRemove(id, out _))
        {
            throw new KeyNotFoundException($"Entity with id {id} not found");
        }
        
        return Task.CompletedTask;
    }

    public Task<IEnumerable<T>> FindWhereAsync(Func<T, bool> predicate, CancellationToken cancellationToken = default)
    {
        var results = _storage.Values.Where(predicate);
        return Task.FromResult(results);
    }
}
