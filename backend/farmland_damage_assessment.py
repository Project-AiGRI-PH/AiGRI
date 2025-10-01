import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import torch
import torchvision.transforms as transforms
from torchvision.models.segmentation import deeplabv3_resnet101, DeepLabV3_ResNet101_Weights
import os

class FarmlandDamageAssessor:
    def __init__(self):
        """Initialize the damage assessment model"""
        # Load pretrained DeepLabV3 model with updated weights parameter
        weights = DeepLabV3_ResNet101_Weights.DEFAULT
        self.model = deeplabv3_resnet101(weights=weights)
        self.model.eval()
        
        # Image preprocessing
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    # Noting on documentation notes
    def load_image(self, image_path):
        """Load and preprocess image with proper error handling"""

        # Early checks for provided image path
        if not os.path.exists(image_path):
            raise FileNotFoundError(
                f"\n{'='*60}\n"
                f"ERROR: Image file not found!\n"
                f"{'='*60}\n"
                f"Looking for: {image_path}\n"
                f"Current directory: {os.getcwd()}\n"
                f"{'='*60}\n"
                f"Please check:\n"
                f"1. The file exists at the specified location\n"
                f"2. The filename is spelled correctly\n"
                f"3. You have the correct path\n"
                f"{'='*60}\n"
            )
        
        img = cv2.imread(image_path) # cv2.imread() method loads an image from the specified file.
        
        # Loaded successfully?
        if img is None:
            raise ValueError(
                f"\n{'='*60}\n"
                f"ERROR: Failed to load image!\n"
                f"{'='*60}\n"
                f"File path: {image_path}\n"
                f"The file exists but couldn't be read as an image.\n"
                f"Please ensure it's a valid image format (JPG, PNG, BMP, etc.)\n"
                f"{'='*60}\n"
            )
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) ### converts BGR image to RGB
        print(f"[OK] Image loaded successfully: {img_rgb.shape[1]}x{img_rgb.shape[0]} pixels")
        return img, img_rgb ### Note on return item: returns both BGR and RGB versions
    
    def segment_image(self, img_rgb):
        """Perform semantic segmentation"""

        # PyTorch .unsqueeze()
        ### Visualizaion: Example 1 - https://www.geeksforgeeks.org/machine-learning/what-does-unsqueeze-do-in-pytorch/
        input_tensor = self.transform(img_rgb)
        input_batch = input_tensor.unsqueeze(0)
        
        ### Perform inference
        with torch.no_grad():
            output = self.model(input_batch)['out'][0]
        
        output_predictions = output.argmax(0).byte().cpu().numpy()
        return output_predictions
    
    def analyze_vegetation_health(self, img_rgb):
        """Analyze vegetation health using color analysis"""

        hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV) # RGB to HSV
        
        ### Define color ranges for vegetation states
        
        # Healthy vegetation (green)
        healthy_lower = np.array([35, 40, 40])
        healthy_upper = np.array([85, 255, 255])
        
        # Partially damaged (yellow-brown)
        partial_lower = np.array([15, 40, 40])
        partial_upper = np.array([35, 255, 255])
        
        # Create masks
        # The ff. returns img files/generates img files
        healthy_mask = cv2.inRange(hsv, healthy_lower, healthy_upper)
        partial_mask = cv2.inRange(hsv, partial_lower, partial_upper)
        
        '''
            Damage map analogy

            - cv2.bitwise_or() is an OpenCV function that performs a bitwise OR operation on two input images 
            - it compares the corresponding pixels of the two input images, bit by bit, and outputs a new image where each pixel's value is the result of the OR operation.
            
            The bitwise OR operation follows these rules for each corresponding bit:
                - If both bits are 0, the result is 0.
            - If one bit is 0 and the other is 1, the result is 1.
            - If both bits are 1, the result is 1.
        '''

        # Fully damaged is everything else (very low saturation or differents hue)
        damaged_mask = 255 - cv2.bitwise_or(healthy_mask, partial_mask)
        
        return healthy_mask, partial_mask, damaged_mask
    
    # Map creation
    def create_damage_map(self, img_rgb, healthy_mask, partial_mask, damaged_mask):
        """Create a color-coded damage map"""
        h, w = img_rgb.shape[:2]
        damage_map = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Color coding:
        # Green = No damage (healthy)
        # Yellow = Partial damage
        # Red = Fully damaged
        damage_map[healthy_mask > 0] = [0, 255, 0]  # Green
        damage_map[partial_mask > 0] = [255, 255, 0]  # Yellow
        damage_map[damaged_mask > 0] = [255, 0, 0]  # Red
        
        # Create overlay
        overlay = cv2.addWeighted(img_rgb, 0.6, damage_map, 0.4, 0)
        
        return damage_map, overlay
    
    # Rough calculation basis
    def calculate_damage_statistics(self, healthy_mask, partial_mask, damaged_mask):
        """Calculate percentage of each damage category"""
        total_pixels = healthy_mask.size
        
        healthy_pixels = np.count_nonzero(healthy_mask)
        partial_pixels = np.count_nonzero(partial_mask)
        damaged_pixels = np.count_nonzero(damaged_mask)
        
        healthy_pct = (healthy_pixels / total_pixels) * 100
        partial_pct = (partial_pixels / total_pixels) * 100
        damaged_pct = (damaged_pixels / total_pixels) * 100
        
        # Determine overall damage level
        if damaged_pct > 50:
            overall_status = "FULLY DAMAGED"
        elif partial_pct + damaged_pct > 50:
            overall_status = "PARTIALLY DAMAGED"
        else:
            overall_status = "NO SIGNIFICANT DAMAGE"
        
        return {
            'healthy_pct': healthy_pct,
            'partial_pct': partial_pct,
            'damaged_pct': damaged_pct,
            'overall_status': overall_status
        }
    
    # Visualization purposes
    def visualize_results(self, img_rgb, damage_map, overlay, stats):
        """Create visualization of results"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Original image
        axes[0, 0].imshow(img_rgb)
        axes[0, 0].set_title('Original Farmland Image', fontsize=14, fontweight='bold')
        axes[0, 0].axis('off')
        
        # Damage map
        axes[0, 1].imshow(damage_map)
        axes[0, 1].set_title('Damage Map\n(Green=Healthy, Yellow=Partial, Red=Damaged)', 
                            fontsize=14, fontweight='bold')
        axes[0, 1].axis('off')
        
        # Overlay
        axes[1, 0].imshow(overlay)
        axes[1, 0].set_title('Damage Overlay', fontsize=14, fontweight='bold')
        axes[1, 0].axis('off')
        
        # Statistics
        axes[1, 1].axis('off')
        stats_text = f"""
        DAMAGE ASSESSMENT REPORT
        ========================
        
        Overall Status: {stats['overall_status']}
        
        Detailed Breakdown:
        • Healthy Area: {stats['healthy_pct']:.2f}%
        • Partially Damaged: {stats['partial_pct']:.2f}%
        • Fully Damaged: {stats['damaged_pct']:.2f}%
        
        Total Area Affected: {stats['partial_pct'] + stats['damaged_pct']:.2f}%
        """
        
        axes[1, 1].text(0.1, 0.5, stats_text, fontsize=12, 
                       verticalalignment='center', fontfamily='monospace',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        return fig
    
    def assess_damage(self, image_path, output_path='damage_assessment.png'):
        """Main function to assess farmland damage"""
        print(f"\nLoading image: {image_path}")
        img, img_rgb = self.load_image(image_path)
        
        print("Analyzing vegetation health...")
        healthy_mask, partial_mask, damaged_mask = self.analyze_vegetation_health(img_rgb)
        
        print("Creating damage map...")
        damage_map, overlay = self.create_damage_map(
            img_rgb, healthy_mask, partial_mask, damaged_mask
        )
        
        print("Calculating statistics...")
        stats = self.calculate_damage_statistics(
            healthy_mask, partial_mask, damaged_mask
        )
        
        print("\n" + "="*50)
        print(f"OVERALL STATUS: {stats['overall_status']}")
        print("="*50)
        print(f"Healthy Area: {stats['healthy_pct']:.2f}%")
        print(f"Partially Damaged: {stats['partial_pct']:.2f}%")
        print(f"Fully Damaged: {stats['damaged_pct']:.2f}%")
        print("="*50)
        
        print("\nGenerating visualization...")
        fig = self.visualize_results(img_rgb, damage_map, overlay, stats)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"[OK] Results saved to: {output_path}")
        # plt.show()
        
        return damage_map, stats

# Example usage
if __name__ == "__main__":
    print("Initializing...")