import { Injectable } from "@angular/core";
import { Photo, PhotoEntity } from "../entity/photo";
import { ApiService } from "./api.service";
import { Subject } from "rxjs";
import { Folder, FolderEntity } from "../entity/folder";

@Injectable({
  providedIn: "root"
})
export class ImageService {

  public images: Photo[] = [];
  public folders: Folder[] = [];
  private ids: string[] = [];

  public folder: string = "";
  public filter: string = "";
  public face: string = "";
  public page: number = 0;

  private findId: string = "";

  private loadingSubject = new Subject<boolean>();
  loading = this.loadingSubject.asObservable();

  private selectedSubject = new Subject<string | null | undefined>();
  selected = this.selectedSubject.asObservable();

  constructor(
    private api: ApiService
  ) {
  }

  startLoader() {
    this.loadingSubject.next(true);
  }

  endLoader() {
    this.loadingSubject.next(false);
  }

  setPage(page = 0) {
    this.page = page;
  }

  setFilter(filter: string = "") {
    if (this.filter && this.filter != filter) {
      this.clear();
    }
    this.filter = filter;
  }

  setFace(face: string = "") {
    if (this.face && this.face != face) {
      this.clear();
    }
    this.face = face;
  }

  setFolder(folder: string = "") {
    if (this.folder && this.folder != folder) {
      this.clear();
    }
    this.folder = folder;
  }

  loadFolders(): Promise<boolean> {
    return new Promise((resolve, reject) => {
      this.api
        .folders()
        .subscribe({
          next: (data) => {
            const folders = data as FolderEntity[];
            if (!folders.length) {
              return reject("nothing to load");
            }
            folders.forEach(data => {
              const folder = new Folder(data);
              this.folders.push(folder);
            });
            resolve(true);
          }, error: (err) => {
            reject(err);
          }
        });
    });
  }

  load(): Promise<boolean> {
    return new Promise((resolve, reject) => {
      this.api
        .photos(++this.page, this.filter, this.folder, this.face)
        .subscribe({
          next: (data) => {
            const photos = data as PhotoEntity[];
            if (!photos.length) {
              return reject("nothing to load");
            }
            photos.forEach(photo => {
              const image = new Photo(photo);
              this.ids.push(image.id);
              this.images.push((image));
            });
            resolve(true);
          }, error: (err) => {
            reject(err);
          }
        });
    });
  }


  byId(id: string): Promise<Photo | null | undefined> {
    return new Promise((resolve) => {
      let res = null;
      if (this.ids.includes(id)) {
        res = this.images.find(i => i.id == id);
        return resolve(res);
      }
      (async () => {
        let res = null;
        while (res === null) {
          res = await this.loadId(id).catch(() => (res = undefined));
        }
        return resolve(res);
      })();
    });
  }

  private async loadId(id: string): Promise<Photo | null | undefined> {
    return new Promise((resolve, reject) => {
      this.load().then((res) => {
        if (!res) {
          reject("No more photos to load");
        } else {
          if (this.ids.includes(id)) {
            return resolve(this.images.find(i => i.id == id));
          } else {
            return resolve(null);
          }
        }
      });
    });
  }


  clear() {
    this.images = [];
    this.page = 0;
    this.filter = "";
  }

  previous(id: string) {
    const idx = Math.max(0, this.ids.indexOf(id) - 1);
    return this.ids[idx];
  }

  next(id: string) {
    const idx = Math.max(0, this.ids.indexOf(id) + 1);
    return this.ids[idx];
  }

  async select(id: string) {
    this.selectedSubject.next(id);
  }

  async unselect() {
    this.selectedSubject.next(null);
  }
}
