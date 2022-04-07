import { Injectable } from "@angular/core";
import { Photo, PhotoEntity } from "../entity/photo";
import { PhotosService } from "./photos.service";
import { Subject } from "rxjs";

@Injectable({
  providedIn: "root"
})
export class ImageService {

  public images: Photo[] = [];
  private ids: string[] = [];

  private loadingSubject = new Subject<boolean>();
  loading = this.loadingSubject.asObservable();

  constructor(
    private photoService: PhotosService
  ) {
  }

  append(photos: PhotoEntity[]) {
    photos.forEach(photo => {
      const image = new Photo(photo);
      this.ids.push(image.id);
      this.images.push((image));
    });
  }

  startLoader() {
    this.loadingSubject.next(true);
  }

  endLoader() {
    this.loadingSubject.next(false);
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
          reject()
        }
      });
    });
  }

  previous(id: string) {
    const idx = Math.max(0, this.ids.indexOf(id) - 1);
    return this.ids[idx];
  }

  next(id: string) {
    const idx = Math.max(0, this.ids.indexOf(id) +1);
    return this.ids[idx];

  }
}
