export interface PhotoInfoEntity {
  pixel_x_dimension: number;
  pixel_y_dimension: number;
}

export interface PhotoEntity {
  folder: string;
  full: string;
  thumb: string;
  timestamp: string;
  info: PhotoInfoEntity;
}
