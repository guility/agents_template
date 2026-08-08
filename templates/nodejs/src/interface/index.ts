/** Interface layer - Controllers и DTOs */

import { UseCase, DTO } from '../application';

// Базовый Response DTO
export class ResponseDTO<T = unknown> extends DTO {
  readonly success: boolean;
  readonly data?: T;
  readonly error?: string;
  readonly timestamp: Date;

  constructor(success: boolean, data?: T, error?: string) {
    super();
    this.success = success;
    this.data = data;
    this.error = error;
    this.timestamp = new Date();
    Object.freeze(this);
  }
}

// Request DTO базовый класс
export abstract class RequestDTO extends DTO {
  abstract validate(): boolean;
}

// Base Controller
export abstract class Controller {
  protected async handleRequest<TReq extends RequestDTO, TRes>(
    request: TReq,
    useCase: UseCase<TReq, TRes>
  ): Promise<ResponseDTO<TRes>> {
    if (!request.validate()) {
      return new ResponseDTO<TRes>(false, undefined, 'Invalid request');
    }

    try {
      const result = await useCase.execute(request);
      return new ResponseDTO<TRes>(true, result);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return new ResponseDTO<TRes>(false, undefined, errorMessage);
    }
  }
}
