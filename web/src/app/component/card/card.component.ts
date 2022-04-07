import { Component, Input } from "@angular/core";
import { Photo } from "../../entity/photo";
import { Router } from "@angular/router";
import { ImageService } from "../../service/image.service";

@Component({
  selector: "app-card",
  templateUrl: "./card.component.html",
  styleUrls: ["./card.component.scss"]
})
export class CardComponent {

  @Input() image?: Photo;

  constructor(
    private router: Router,
    private imageService: ImageService
  ) {
  }

  style(): { [key: string]: string } {
    return {
      "background-image": `url("${this.image?.thumb}")`,
      "background-size": "cover"
    };
  }

  onClick() {
    this.imageService.startLoader();
    this.router.navigate(['full-view', this.image?.id]);
  }
}
