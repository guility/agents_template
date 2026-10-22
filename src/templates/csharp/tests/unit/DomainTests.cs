namespace DddTemplate.Tests.Unit.Domain;

using System;
using DddTemplate.Domain;
using Xunit;

public class BaseEntityTests
{
    [Fact]
    public void Constructor_ShouldSetId_WhenCreated()
    {
        // Arrange & Act
        var entity = new TestEntity();

        // Assert
        Assert.NotNull(entity.Id);
        Assert.NotEmpty(entity.Id);
    }

    [Fact]
    public void Constructor_ShouldSetCreatedAt_WhenCreated()
    {
        // Arrange
        var before = DateTime.UtcNow;

        // Act
        var entity = new TestEntity();

        // Assert
        Assert.True(entity.CreatedAt >= before);
        Assert.True(entity.CreatedAt <= DateTime.UtcNow);
    }

    [Fact]
    public void Constructor_ShouldSetUpdatedAt_WhenCreated()
    {
        // Arrange
        var before = DateTime.UtcNow;

        // Act
        var entity = new TestEntity();

        // Assert
        Assert.True(entity.UpdatedAt >= before);
        Assert.True(entity.UpdatedAt <= DateTime.UtcNow);
    }

    [Fact]
    public void MarkAsModified_ShouldUpdateUpdatedAt_WhenCalled()
    {
        // Arrange
        var entity = new TestEntity();
        var beforeUpdate = entity.UpdatedAt;

        // Act - wait a small amount to ensure time difference
        System.Threading.Thread.Sleep(10);
        entity.MarkAsModified();

        // Assert
        Assert.True(entity.UpdatedAt > beforeUpdate);
    }

    [Fact]
    public void CreatedAt_AndUpdatedAt_ShouldBeEqual_Initially()
    {
        // Arrange & Act
        var entity = new TestEntity();

        // Assert
        Assert.Equal(entity.CreatedAt, entity.UpdatedAt);
    }
}

// Test implementation for abstract BaseEntity
public class TestEntity : BaseEntity
{
    public void Validate()
    {
        // Implementation for testing
    }
}
