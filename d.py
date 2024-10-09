import math
import struct
import bitarray
import argparse

PI = math.pi
RADIUS_SCALE = 0.56418958354775628694807945156085

class CircleNode:
    def __init__(self, value, angle_start, angle_end, error_threshold=0.1):
        self.value = value
        self.angle_start = angle_start
        self.angle_end = angle_end
        self.error_threshold = error_threshold
        self.left = None
        self.right = None

class CircleTree:
    def __init__(self):
        self.root = None

    def insert(self, value):
        angle = data_to_angle(value)
        if not self.root:
            self.root = CircleNode(value, 0, 2 * PI)
        else:
            self._insert_recursive(self.root, value, angle)

    def _insert_recursive(self, node, value, angle):
        mid_angle = (node.angle_start + node.angle_end) / 2
        if angle < mid_angle:
            if node.left:
                self._insert_recursive(node.left, value, angle)
            else:
                node.left = CircleNode(value, node.angle_start, mid_angle)
        else:
            if node.right:
                self._insert_recursive(node.right, value, angle)
            else:
                node.right = CircleNode(value, mid_angle, node.angle_end)

    def find_closest(self, angle):
        return self._find_closest_recursive(self.root, angle)

    def _find_closest_recursive(self, node, angle):
        if not node:
            return None
        mid_angle = (node.angle_start + node.angle_end) / 2
        if angle < mid_angle:
            closer = self._find_closest_recursive(node.left, angle)
        else:
            closer = self._find_closest_recursive(node.right, angle)
        
        if closer is None or abs(data_to_angle(node.value) - angle) < abs(data_to_angle(closer.value) - angle):
            return node
        return closer

def data_to_angle(value):
    return 2 * PI * (value / 256)

def angle_to_data(angle):
    return int((angle / (2 * PI)) * 256)

def compress(input_file, output_file):
    with open(input_file, 'rb') as f:
        data = f.read()
    
    tree = CircleTree()
    bit_stream = bitarray.bitarray()
    error_stream = bytearray()
    
    for byte in data:
        angle = data_to_angle(byte)
        closest_node = tree.find_closest(angle)
        
        if closest_node and abs(closest_node.value - byte) <= closest_node.error_threshold * 256:
            bit_stream.append(1)
        else:
            bit_stream.append(0)
            error_stream.append(byte)
        
        tree.insert(byte)
    
    with open(output_file, 'wb') as f:
        bit_stream.tofile(f)
        f.write(error_stream)

def decompress(input_file, output_file):
    with open(input_file, 'rb') as f:
        bit_stream = bitarray.bitarray()
        bit_stream.fromfile(f)
        error_stream = f.read()
    
    tree = CircleTree()
    output = bytearray()
    error_index = 0
    
    for bit in bit_stream:
        if bit:
            angle = data_to_angle(output[-1]) if output else 0
            closest_node = tree.find_closest(angle)
            byte = closest_node.value if closest_node else 0
        else:
            byte = error_stream[error_index]
            error_index += 1
        
        output.append(byte)
        tree.insert(byte)
    
    with open(output_file, 'wb') as f:
        f.write(output)

def main():
    parser = argparse.ArgumentParser(description='Compress or decompress a file using circle mapping.')
    parser.add_argument('action', choices=['compress', 'decompress'], help='Action to perform')
    parser.add_argument('input_file', help='Input file path')
    parser.add_argument('output_file', help='Output file path')
    
    args = parser.parse_args()
    
    if args.action == 'compress':
        compress(args.input_file, args.output_file)
        print(f"Compressed {args.input_file} to {args.output_file}")
    else:
        decompress(args.input_file, args.output_file)
        print(f"Decompressed {args.input_file} to {args.output_file}")

if __name__ == "__main__":
    main()
