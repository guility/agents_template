/** Infrastructure layer - реализация портов */

import { Entity, BaseEntity } from '../domain';
import { Repository } from '../application';

// In-Memory Repository для тестирования
export class InMemoryRepository<T extends Entity> implements Repository<T> {
  protected storage: Map<string, T> = new Map();

  async findById(id: string): Promise<T | null> {
    return this.storage.get(id) || null;
  }

  async findAll(): Promise<T[]> {
    return Array.from(this.storage.values());
  }

  async save(entity: T): Promise<void> {
    this.storage.set(entity.id, entity);
  }

  async delete(id: string): Promise<void> {
    this.storage.delete(id);
  }
}

// Logger implementation
export class ConsoleLogger {
  info(message: string): void {
    console.log(`[INFO] ${message}`);
  }

  error(message: string): void {
    console.error(`[ERROR] ${message}`);
  }

  warn(message: string): void {
    console.warn(`[WARN] ${message}`);
  }
}
