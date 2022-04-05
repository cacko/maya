import { Injectable } from "@angular/core";
import { Image } from "../entity/image";
import { PhotoEntity } from "../entity/photo";
import { PhotosService } from "./photos.service";

@Injectable({
  providedIn: "root"
})
export class ImageService {

  public images: Image[] = [];
  private ids: string[] = [];

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
    return new Promise((resolve, reject) => {
      if (this.ids.includes(id)) {
        return resolve(this.images.find(i => i.id == id));
      }
      this.photoService.photos.subscribe(data => {
        const items = data as PhotoEntity[];
        items.forEach(i => {
          const image = new Image(i);
          if (image.id == id) {
            return resolve(image);
          }
        });
        this.photoService.load(++this.photoService.page);
      });
    });
  }

}
