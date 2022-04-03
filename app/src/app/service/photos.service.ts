import { Injectable } from "@angular/core";
import { Firestore } from "@angular/fire/firestore";
import { AngularFirestore, AngularFirestoreCollection } from "@angular/fire/compat/firestore";
import { Subject } from "rxjs";
import { PhotoEntity } from "../entity/photo";

@Injectable({
  providedIn: "root"
})
export class PhotosService {

  private photosSubject = new Subject<PhotoEntity[]>();
  photos = this.photosSubject.asObservable();

  constructor(
    private afs: AngularFirestore
  ) {

  }

  load() {
    const ref = this.afs.collection("photos",
      ref => ref.orderBy("timestamp", "desc").limit(50)).valueChanges();
    ref.subscribe((items) => {
      console.log(items);
      const data = items as PhotoEntity[];
      this.photosSubject.next(data);
    });
  }
}
