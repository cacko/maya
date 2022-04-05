import { PhotoEntity } from "./photo";



import { Md5 } from "ts-md5/dist/md5";

export class Image {

  private data: PhotoEntity;
  private readonly CDN_HOST = "https://cdn.cacko.net";

  constructor(data: PhotoEntity) {
    this.data = data;
  }

  public get id(): string {
    return Md5.hashStr(this.data.full);
  }

  public get thumb(): string {
    return `${this.CDN_HOST}/${this.data.thumb}`;
  }

  public get src(): string {
    return `${this.CDN_HOST}/${this.data.full}`;
  }

  public get style(): string {
    const ratio = this.data.width / this.data.height;

    if (ratio > 4 / 3) {
      return "card-wide";
    }

    if (ratio < 3 / 4) {
      return "card-tall";
    }

    return "";
  }


}
