/** Application layer - Use Cases и Ports (интерфейсы) */

import { Entity } from '../domain';

// Repository Port - интерфейс для репозиториев
export interface Repository<T extends Entity> {
  findById(id: string): Promise<T | null>;
  findAll(): Promise<T[]>;
  save(entity: T): Promise<void>;
  delete(id: string): Promise<void>;
}

// Use Case интерфейс
export interface UseCase<TRequest, TResponse> {
  execute(request: TRequest): Promise<TResponse>;
}

// DTO базовый класс
export abstract class DTO {
  constructor() {
    Object.freeze(this);
  }
}
