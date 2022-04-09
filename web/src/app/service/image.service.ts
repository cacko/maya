import { Injectable } from "@angular/core";
import { Photo, PhotoEntity } from "../entity/photo";
import { ApiService } from "./api.service";
import { Subject } from "rxjs";

@Injectable({
  providedIn: "root"
})
export class ImageService {

  public images: Photo[] = [];
  private ids: string[] = [];

  public folder: string = "";
  public filter: string = "";
  public page: number = 0;

  private loadingSubject = new Subject<boolean>();
  loading = this.loadingSubject.asObservable();

  private selectedSubject = new Subject<string | null | undefined>();
  selected = this.selectedSubject.asObservable();

  constructor(
    private photoService: ApiService
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

  setFolder(folder: string = "") {
    if (this.folder && this.filter != folder) {
      this.clear();
    }
    this.filter = folder;
  }

  load(): Promise<boolean> {
    return new Promise((resolve) => {
      this.photoService.photos.subscribe((data) => {
        const photos = data as PhotoEntity[];
        photos.forEach(photo => {
          const image = new Photo(photo);
          this.ids.push(image.id);
          this.images.push((image));
        });
        resolve(true);
      });
      this.photoService.load(++this.page, this.filter, this.folder);
    });
  }

  byId(id: string): Promise<Photo | undefined> {
    return new Promise((resolve, reject) => {
      if (this.ids.includes(id)) {
        return resolve(this.images.find(i => i.id == id));
      }
      this.photoService.photos.subscribe(data => {
        const items = data as PhotoEntity[];
        items.forEach(i => {
          const image = new Photo(i);
          if (image.id == id) {
            return resolve(image);
          }
        });
        try {
          this.photoService.load(++this.photoService.page);
        } catch (err) {
          reject();
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
