namespace DddTemplate.Domain;

using System;

/// <summary>
/// Base class for all domain entities following DDD principles
/// </summary>
public abstract class BaseEntity
{
    public string Id { get; protected set; } = Guid.NewGuid().ToString();
    public DateTime CreatedAt { get; protected set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; protected set; } = DateTime.UtcNow;

    public void MarkAsModified()
    {
        UpdatedAt = DateTime.UtcNow;
    }
}

/// <summary>
/// Interface for domain entities
/// </summary>
public interface IEntity
{
    string Id { get; }
    DateTime CreatedAt { get; }
    DateTime UpdatedAt { get; }
    void Validate();
}

/// <summary>
/// Base class for value objects in DDD
/// </summary>
public abstract class ValueObject
{
    public abstract override bool Equals(object? obj);
    public abstract override int GetHashCode();

    protected static bool EqualOperator(ValueObject left, ValueObject right)
    {
        if (left is null ^ right is null)
            return false;
        return left is null || left.Equals(right!);
    }

    protected static bool NotEqualOperator(ValueObject left, ValueObject right)
        => !EqualOperator(left, right);
}
