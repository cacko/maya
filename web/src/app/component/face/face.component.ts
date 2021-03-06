import {Component, Input} from '@angular/core';
import {FaceEntity} from "../../entity/face";
import {ImageService} from "../../service/image.service";
import {capitalize} from "lodash-es";


@Component({
  selector: 'app-face',
  templateUrl: './face.component.html',
  styleUrls: ['./face.component.scss']
})
export class FaceComponent {

  @Input() face: FaceEntity | null = null;

  constructor(
    public imageService: ImageService
  ) {
  }


  getImageStyle(): { [key: string]: string } {
    return {
      'background-image': `url("data:image/webp;base64,${this.face?.image}")`,
    };
  }

  get tooltip(): string {
    return capitalize(this.face?.name);
  }

  get link() {
    if (this.imageService.face == this.face?.name) {
      return "/";
    }
    return `/face/${this.face?.name}`;
  }


}
