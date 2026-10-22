/** Unit tests для domain layer */

import { BaseEntity, ValueObject, Entity } from '../../src/domain';

class TestEntity extends Entity {
  validate(): boolean {
    return this.id.length > 0;
  }
}

describe('BaseEntity', () => {
  it('should create entity with id', () => {
    const entity = new BaseEntity('test-123');
    expect(entity.id).toBe('test-123');
  });

  it('should set createdAt automatically', () => {
    const entity = new BaseEntity('test-123');
    expect(entity.createdAt).toBeInstanceOf(Date);
  });

  it('should update timestamp on updateTimestamp', () => {
    const entity = new BaseEntity('test-123');
    const oldTimestamp = entity.updatedAt;
    
    setTimeout(() => {
      entity.updateTimestamp();
      expect(entity.updatedAt).not.toBe(oldTimestamp);
    }, 10);
  });
});

describe('ValueObject', () => {
  it('should be immutable (frozen)', () => {
    const vo = new ValueObject();
    expect(Object.isFrozen(vo)).toBe(true);
  });
});

describe('Entity', () => {
  it('should create entity extending BaseEntity', () => {
    const entity = new TestEntity('entity-1');
    expect(entity).toBeInstanceOf(BaseEntity);
    expect(entity.id).toBe('entity-1');
  });

  it('should validate correctly', () => {
    const validEntity = new TestEntity('valid-id');
    expect(validEntity.validate()).toBe(true);

    const invalidEntity = new TestEntity('');
    expect(invalidEntity.validate()).toBe(false);
  });
});
