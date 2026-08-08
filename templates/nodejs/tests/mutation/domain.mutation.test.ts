/** Mutation tests для domain layer.

Каждая функция должна иметь минимум 2 мутации.
*/

import { BaseEntity, Entity } from '../../src/domain';

class TestEntity extends Entity {
  validate(): boolean {
    return this.id.length > 0;
  }
}

describe('BaseEntity Mutations', () => {
  it('MUTATION-1: createdAt should be set in constructor', () => {
    // Мутация 1: Если убрать установку createdAt
    const entity = new BaseEntity('test-1');
    expect(entity.createdAt).toBeDefined();
    expect(entity.createdAt).toBeInstanceOf(Date);
  });

  it('MUTATION-2: updateTimestamp should change updatedAt', () => {
    // Мутация 2: Если updateTimestamp не меняет updatedAt
    const entity = new BaseEntity('test-1');
    const beforeUpdate = entity.updatedAt;
    
    // Даем времени пройти
    const wait = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));
    
    return wait(10).then(() => {
      entity.updateTimestamp();
      expect(entity.updatedAt).not.toBe(beforeUpdate);
    });
  });
});

describe('Entity Mutations', () => {
  it('MUTATION-1: validate should check id length', () => {
    // Мутация 1: Если validate всегда возвращает true
    const validEntity = new TestEntity('valid-id');
    expect(validEntity.validate()).toBe(true);

    const invalidEntity = new TestEntity('');
    expect(invalidEntity.validate()).toBe(false);
  });

  it('MUTATION-2: Entity should inherit from BaseEntity', () => {
    // Мутация 2: Если Entity не наследуется от BaseEntity
    const entity = new TestEntity('entity-1');
    expect(entity).toBeInstanceOf(BaseEntity);
    expect(entity.createdAt).toBeDefined();
  });
});
