import {Injectable} from '@angular/core';
import {ApiService} from "./api.service";
import {FaceEntity} from "../entity/face";

@Injectable({
  providedIn: 'root'
})
export class FaceService {

  public faces: FaceEntity[]|null = null;

  constructor(
    private api: ApiService
  ) {
  }


  load(): Promise<boolean> {
    return new Promise((resolve, reject) => {
      if (this.faces !== null) {
        return resolve(true);
      }
      this.api
        .faces()
        .subscribe({
          next: (data) => {
            const faces = data as FaceEntity[];
            if (!faces.length) {
              return reject("nothing to load");
            }
            this.faces = faces;
            resolve(true);
          }, error: (err) => {
            reject(err);
          }
        });
    });
  }

}
