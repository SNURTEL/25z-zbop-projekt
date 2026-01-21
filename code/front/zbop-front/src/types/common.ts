// Common types based on OpenAPI specification

export interface ErrorResponse {
  detail: string;
}

export interface ValidationErrorItem {
  loc: string[];
  msg: string;
  type: string;
}

export interface ValidationError {
  detail: ValidationErrorItem[];
}
