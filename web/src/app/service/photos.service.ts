import { Injectable } from "@angular/core";
import { Subject } from "rxjs";
import { PhotoEntity } from "../entity/photo";

@Injectable({
  providedIn: "root"
})
export class PhotosService {

  private photosSubject = new Subject<PhotoEntity[]>();
  photos = this.photosSubject.asObservable();

  constructor(
  ) {

  }

  load() {

  }
}
