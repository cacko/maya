import { Injectable } from "@angular/core";
import { Image } from "../entity/image";
import { PhotoEntity } from "../entity/photo";
import { PhotosService } from "./photos.service";
import { Subject } from "rxjs";

@Injectable({
  providedIn: "root"
})
export class ImageService {

  public images: Image[] = [];
  private ids: string[] = [];

  private loadingSubject = new Subject<boolean>();
  loading = this.loadingSubject.asObservable();

  constructor(
    private photoService: PhotosService
  ) {
  }

  append(photos: PhotoEntity[]) {
    photos.forEach(photo => {
      const image = new Image(photo);
      this.ids.push(image.id);
      this.images.push((image));
    });
  }

  byId(id: string): Promise<Image | undefined> {
    this.loadingSubject.next(true);
    return new Promise((resolve, reject) => {
      if (this.ids.includes(id)) {
        this.loadingSubject.next(false);
        return resolve(this.images.find(i => i.id == id));
      }
      this.photoService.photos.subscribe(data => {
        const items = data as PhotoEntity[];
        items.forEach(i => {
          const image = new Image(i);
          if (image.id == id) {
            this.loadingSubject.next(false);
            return resolve(image);
          }
        });
        this.photoService.load(++this.photoService.page);
      });
    });
  }

}
