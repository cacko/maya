import { PhotoEntity } from "./photo";

export class Image {

  private data: PhotoEntity;
  private readonly CDN_HOST = "https://cdn.cacko.net";

  constructor(data: PhotoEntity) {
    this.data = data;
  }

  public get thumb(): string {
    return `${this.CDN_HOST}/${this.data.thumb}`;
  }

  public get src(): string {
    return `${this.CDN_HOST}/${this.data.full}`;
  }

  public get style(): string {
    const ratio = this.data.info.pixel_x_dimension / this.data.info.pixel_y_dimension;

    if (ratio > 16 / 9) {
      return "card-wide";
    }

    if (ratio < 3 / 4) {
      return "card-tall";
    }

    return "";
  }


}
