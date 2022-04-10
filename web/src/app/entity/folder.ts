import { Photo, PhotoEntity } from "./photo";
import { Md5 } from "ts-md5/dist/md5";

export interface FolderEntity {
  folder: string;
  count: number;
  sample: PhotoEntity[];
}


export class Folder {

  private data: FolderEntity;

  constructor(data: FolderEntity) {
    this.data = data;
  }

  public get name(): string {
    return this.data.folder;
  }

  public get size(): number {
    return this.data.count;
  }

  public get id(): string {
    return "a" + Md5.hashStr(this.data.folder);
  }

  public get photos(): Photo[] {
    return this.data.sample.map(a => (new Photo(a)));
  }

}
