import React from "react";
import { Anchor, Group, Progress, Table, Text } from "@mantine/core";
import classes from "./TableReviews.module.css";

type Row = {
  image: string;
  emotions?: string;
  timestap?: number | string;
  reviews: { positive: number; negative: number };
};

export function TableReviews({ rows = [] as Row[] }: { rows?: Row[] }) {
  // eslint: require braces for single-line ifs
  if (!rows || rows.length === 0) {
    return null; // do not render when empty
  }

  const trs = rows.map((row) => {
    const totalReviews = row.reviews.positive + row.reviews.negative;
    const positive = totalReviews > 0 ? (row.reviews.positive / totalReviews) * 100 : 0;
    const negative = totalReviews > 0 ? (row.reviews.negative / totalReviews) * 100 : 0;

    return (
      <Table.Tr key={row.image + (row.timestap ?? "")}>
        <Table.Td>
          <Anchor component="button" fz="sm">
            {row.image}
          </Anchor>
        </Table.Td>
        <Table.Td>{row.timestap ?? "-"}</Table.Td>
        <Table.Td>
          <Anchor component="button" fz="sm">
            {row.emotions ?? "-"}
          </Anchor>
        </Table.Td>
        <Table.Td>{Intl.NumberFormat().format(totalReviews)}</Table.Td>
        <Table.Td>
          <Group justify="space-between">
            <Text fz="xs" c="teal" fw={700}>
              {Math.round(positive)}%
            </Text>
            <Text fz="xs" c="red" fw={700}>
              {Math.round(negative)}%
            </Text>
          </Group>

          <Progress.Root style={{ height: 10, marginTop: 6 }}>
            <Progress.Section className={classes.progressSection} value={positive} color="teal" />
            <Progress.Section className={classes.progressSection} value={negative} color="red" />
          </Progress.Root>
        </Table.Td>
      </Table.Tr>
    );
  });

  return (
    <Table.ScrollContainer minWidth={800}>
      <Table verticalSpacing="xs">
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Image</Table.Th>
            <Table.Th>Timestamp</Table.Th>
            <Table.Th>Emotions</Table.Th>
            <Table.Th>Reviews</Table.Th>
            <Table.Th>Distribution</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>{trs}</Table.Tbody>
      </Table>
    </Table.ScrollContainer>
  );
}

// return (
  //   <ScrollArea style={{ height: 280 }}>
  //     <Table verticalSpacing="xs" striped highlightOnHover>
  //       <thead>
  //         <tr>
  //           <th>image</th>
  //           <th>timestap</th>
  //           <th>emotions</th>
//           <th>Reviews</th>
//           <th>Distribution</th>
//         </tr>
//       </thead>
//       <tbody>{trs}</tbody>
//     </Table>
//   </ScrollArea>
// );
//   return (
//     <tr key={row.image}>
//       <td><Anchor component="button" fz="sm">{row.image}</Anchor></td>
//       <td>{row.timestap ?? "-"}</td>
//       <td><Anchor component="button" fz="sm">{row.emotions ?? "-"}</Anchor></td>
//       <td>{Intl.NumberFormat().format(totalReviews)}</td>
//       <td style={{ width: 240 }}>
//         <Group position="apart" align="center" mb={6}>
//           <Text fz="xs" c="teal" fw={700}>{Math.round(positive)}%</Text>
//           <Text fz="xs" c="red" fw={700}>{Math.round(negative)}%</Text>
//         </Group>

//         <Progress
//           sections={[
//             { value: positive, color: "teal" },
//             { value: negative, color: "red" },
//           ]}
//           size="sm"
//           radius="sm"
//         />
//       </td>
//     </tr>
//   );
// }