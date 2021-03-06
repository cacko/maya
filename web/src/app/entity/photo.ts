export interface PhotoEntity {
  folder: string;
  full: string;
  thumb: string;
  timestamp: string;
  width: number;
  height: number;
  latitude: number;
  longitude: number;
  faces?: string;
  locations?: string;
}


import {Md5} from "ts-md5/dist/md5";

export class Photo {

  private data: PhotoEntity;
  private readonly CDN_HOST = "https://cdn.cacko.net";

  constructor(data: PhotoEntity) {
    this.data = data;
  }

  public get id(): string {
    return 'a' + Md5.hashStr(this.data.full);
  }

  public get thumb(): string {
    return `${this.CDN_HOST}/${this.data.thumb}`;
  }

  public get src(): string {
    return `${this.CDN_HOST}/${this.data.full}`;
  }

  public get aspect(): string {
    return this.data.width > this.data.height ? 'maxHeight' : 'maxWidth';
  }

  public get faces(): string[] {
    if (this.data.faces) {
      return this.data.faces.split(",").map((n) => n.trim());
    }
    return [];
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
