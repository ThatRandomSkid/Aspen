//
//  Item.swift
//  Aspen
//
//  Created by Linden Morgan on 4/5/25.
//

import Foundation
import SwiftData

@Model
final class Item {
    var timestamp: Date
    
    init(timestamp: Date) {
        self.timestamp = timestamp
    }
}
