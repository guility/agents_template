/** Domain layer - бизнес-сущности и логика предметной области */

export abstract class BaseEntity {
  readonly id: string;
  readonly createdAt: Date;
  updatedAt?: Date;

  constructor(id: string) {
    this.id = id;
    this.createdAt = new Date();
  }

  updateTimestamp(): void {
    this.updatedAt = new Date();
  }
}

export abstract class ValueObject {
  // Value Objects неизменяемы по определению
  constructor() {
    Object.freeze(this);
  }
}

export abstract class Entity extends BaseEntity {
  constructor(id: string) {
    super(id);
  }

  abstract validate(): boolean;
}
