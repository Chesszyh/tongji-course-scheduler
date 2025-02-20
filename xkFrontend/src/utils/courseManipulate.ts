// 储存了一些判断是否满足条件的函数

// 一些接口
interface occupyCell {
    code: string;
    occupyWeek: number[];
}

interface arrangementInfolet {
    arrangementText: string;
    occupyDay: number;
    occupyTime: number[];
    occupyWeek: number[];
    occupyRoom: string;
    teacherAndCode: string;
}

// helper function，判断两个数组是否有交集
function hasIntersection(arr1: number[], arr2: number[]): boolean {
    // 下边这行做的是：arr1 是否有一些元素，这些元素是 arr2 的子集
    return arr1.some(item => arr2.includes(item));
}

// 判断是否能够添加课程到课程表中
export function canAddCourse(arrangementInfo: arrangementInfolet[], occupied: occupyCell[][][], code: string) : {canAdd: boolean, collideCourse?: string} {
    // 如果 occupied 中存在 code 与当前课程相同的课程，则返回 true
    
    // console.log("occupied", occupied);
    // console.log("occupied.flat()", occupied.flat());
    // console.log("occupied.flat().flat()", occupied.flat().flat());

    const existingCode = occupied.flat().flat().find(item => isSameCourse(item.code, code))?.code;

    if (existingCode) {
        console.log("触发了相同课号的判断");
        // 如果课号相同，能不能加的标准是，把旧的给删掉之后，有没有冲突
        // 所以创建一份拷贝来判断
        const newOccupied = JSON.parse(JSON.stringify(occupied));
        deleteOccupied(newOccupied, existingCode);
        return canAddCourse(arrangementInfo, newOccupied, code); // recursive~~~
    }

    // arrangementInfo 是 数组
    // occupied 是 12 * 7 的二维数组，每个元素是一个数组，存放了当前时间课程的课号和占用的周
    for (let arr of arrangementInfo) { // 遍历了一门课的全部时间段
        for (let occupyTimelet of arr.occupyTime) { // 遍历了一个时间段的全部时间
            // 如果这个时间段已经被占用了
            if (occupied[occupyTimelet - 1][arr.occupyDay - 1]) {
                // 检查是否与已占用时段的课程有时间冲突
                const collideItem = occupied[occupyTimelet - 1][arr.occupyDay - 1].find(item => 
                    hasIntersection(arr.occupyWeek, item.occupyWeek)
                );
                if (collideItem) {
                    return {
                        canAdd: false,
                        collideCourse: collideItem.code
                    }
                }
            }
        }
    }
    return {
        canAdd: true // 需要满足全部时间段的全部时间都没有被占用
    }
}

// 增
export function insertOccupied(occupied: occupyCell[][][], arrangementInfo: arrangementInfolet[], code: string) {
    for (let arr of arrangementInfo) {
        for (let occupyTimelet of arr.occupyTime) {
            console.log("zhanyong", occupied);
            occupied[occupyTimelet - 1][arr.occupyDay - 1].push({
                code: code,
                occupyWeek: arr.occupyWeek
            });
        }
    }
}

// 删
export function deleteOccupied(occupied: occupyCell[][][], code: string) {
    for (let i = 0; i < 12; i++) {
        for (let j = 0; j < 7; j++) {
            occupied[i][j] = occupied[i][j].filter(item => !isSameCourse(item.code, code));
        }
    }
}

// 改
export function updateOccupied(occupied: occupyCell[][][], arrangementInfo: arrangementInfolet[], code: string) {
    deleteOccupied(occupied, code);
    insertOccupied(occupied, arrangementInfo, code);
}

// 判断两个课是否相同
// 依据是比较课号除了后两位的部分
export function isSameCourse(code1: string, code2: string) {
    return code1?.slice(0, -2) === code2?.slice(0, -2);
}